"""
PADAS CLIPBOARD MANAGER - FILE MAKER ACTIONS
Integrazione con Esplora File e creazione fisica di file e cartelle su disco.
"""

import ctypes
import logging
import winsound
from pathlib import Path
from urllib.parse import unquote, urlparse
from PyQt6.QtWidgets import QMessageBox
from .text_splitter import TextSplitterHelper
from .coordinate_utils import CoordinateUtils


class FileMakerActionsManager:
    """Gestisce l'integrazione con Esplora File e la creazione fisica di file/cartelle tramite composizione."""

    def __init__(self, manager):
        self.manager = manager  # Riceve il riferimento al Manager principale

    @classmethod
    def ottieni_percorso_esplora_risorse_attivo(cls) -> Path | None:
        """
        Rileva la finestra/scheda di Esplora File (Windows Explorer) attualmente attiva
        ed estrae il percorso reale della cartella aperta nella scheda in primo piano.
        """
        try:
            import win32com.client
            user32 = ctypes.windll.user32
            hwnd_attivo = user32.GetForegroundWindow()

            # Recupera il titolo della finestra in primo piano per identificare la scheda attiva
            length = user32.GetWindowTextLengthW(hwnd_attivo)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd_attivo, buf, length + 1)
            titolo_finestra = buf.value.strip().lower()

            shell = win32com.client.Dispatch("Shell.Application")
            candidati = []

            for window in shell.Windows():
                if getattr(window, "HWND", None) == hwnd_attivo:
                    url = getattr(window, "LocationURL", "")
                    loc_name = getattr(window, "LocationName", "").strip().lower()

                    if url.startswith("file:///"):
                        path_str = unquote(urlparse(url).path)
                        if len(path_str) > 2 and path_str[0] == "/" and path_str[2] == ":":
                            path_str = path_str[1:]
                        path_str = path_str.replace("/", "\\")
                        p = Path(path_str)
                        if p.exists() and p.is_dir():
                            candidati.append((p, loc_name))

            if not candidati:
                return None

            # 1. Cerca il candidato la cui scheda o il cui nome cartella corrisponde al titolo della finestra attiva
            for path_obj, loc_name in candidati:
                folder_name = path_obj.name.strip().lower()
                if (loc_name and loc_name in titolo_finestra) or (folder_name and folder_name in titolo_finestra):
                    logging.info(f"[MAKE-FILES] Scheda attiva identificata tramite titolo '{loc_name or folder_name}': {path_obj}")
                    return path_obj

            # 2. Fallback: restituisce l'ultimo candidato presente
            logging.info(f"[MAKE-FILES] Scheda attiva selezionata da fallback: {candidati[-1][0]}")
            return candidati[-1][0]

        except Exception as err:
            logging.warning(f"[MAKE-FILES] Rilevamento Esplora File fallito: {err}")
        return None

    @classmethod
    def crea_file_e_cartelle(cls, slot_inizio: str, param2: str, memoria: list, layout_matrice: list, parent_widget=None):
        """
        Esegue la creazione di file e cartelle fisiche su disco da slot singolo o range di slot (Shift + Alt + M).
        - Rileva automaticamente la scheda attiva di Esplora File.
        - Salva e ripristina la configurazione dell'utente (estensione automatica, modalità cartella).
        """
        cartella_attiva = cls.ottieni_percorso_esplora_risorse_attivo()
        if not cartella_attiva:
            logging.warning("[MAKE-FILES] Nessuna finestra di Esplora File attiva rilevata.")
            if parent_widget:
                QMessageBox.warning(
                    parent_widget,
                    "Esplora File Non Attivo",
                    "<b>Impossibile identificare la cartella di destinazione!</b><br><br>"
                    "Il comando <code>Shift + Alt + M</code> funziona unicamente quando hai in primo piano una finestra di <b>Esplora File (Windows)</b>.<br><br>"
                    "Seleziona o apri la cartella di destinazione in Esplora File e riprova."
                )
            return

        start_clean = slot_inizio.strip().lower()
        param2_clean = param2.strip().lower() if param2 else ""

        elementi_raw = []

        # 1. Estrazione elementi da slot singolo o da intervallo coordinato
        item_inizio = next((e for e in memoria if e.get("slot") == start_clean), None)
        testo_inizio = item_inizio.get("dato", "") if item_inizio else ""

        elementi_da_singolo = TextSplitterHelper.rileva_elementi_file(testo_inizio)

        if not param2_clean and len(elementi_da_singolo) > 1:
            # Caso A: Slot singolo con separatori interni
            elementi_raw = elementi_da_singolo
        else:
            # Caso B: Range di slot (da slot_inizio a param2 o sequenza)
            slot_fine = param2_clean if param2_clean else start_clean
            slot_dettagli, _ = CoordinateUtils.calcola_range_coordinate(start_clean, slot_fine, layout_matrice)

            for dett in slot_dettagli:
                s_name = dett["slot"]
                item = next((e for e in memoria if e.get("slot", "").strip().lower() == s_name), None)
                if item and item.get("dato"):
                    sub_elems = TextSplitterHelper.rileva_elementi_file(item["dato"])
                    elementi_raw.extend(sub_elems if sub_elems else [item["dato"].strip()])

        elementi_puliti = [e.strip() for e in elementi_raw if e.strip()]

        if not elementi_puliti:
            logging.warning(f"[MAKE-FILES] Nessun testo o elemento valido trovato negli slot specificati.")
            if parent_widget:
                QMessageBox.warning(parent_widget, "Creazione File", "Nessun testo o elemento valido trovato negli slot selezionati.")
            return

        # Recupera la configurazione salvata se presente sul parent_widget
        config_make_files = getattr(parent_widget, "config_make_files", {})

        # 2. Pop-up di configurazione modalità destinazione cartella ed estensioni
        from ..dialogs_core import MakeFilesOptionsDialog
        dlg = MakeFilesOptionsDialog(
            elementi_puliti,
            cartella_base=cartella_attiva,
            config=config_make_files,
            parent=parent_widget
        )
        if not dlg.exec():
            return

        # Salva la nuova configurazione nel parent_widget per le successive esecuzioni
        nuova_config = dlg.get_configurazione()
        if parent_widget:
            parent_widget.config_make_files = nuova_config
            if hasattr(parent_widget, "_salva_sessione"):
                parent_widget._salva_sessione()

        cartella_dest, lista_file = dlg.get_cartella_e_file()

        # 3. Creazione fisica delle directory e dei file nella cartella di Esplora File attiva
        cartella_path = cartella_attiva / cartella_dest if cartella_dest else cartella_attiva

        try:
            cartella_path.mkdir(parents=True, exist_ok=True)
            file_creati = 0

            for nome_f in lista_file:
                if not nome_f:
                    continue
                file_p = cartella_path / nome_f
                file_p.parent.mkdir(parents=True, exist_ok=True)
                if not file_p.exists():
                    file_p.touch()
                    file_creati += 1

            try:
                winsound.Beep(1000, 150)
            except Exception:
                pass

            msg = f"<b>Operazione Completata!</b><br><br>" \
                  f"• Cartella di destinazione: <code>{cartella_path}</code><br>" \
                  f"• Nuovi file creati su disco: <b>{file_creati}</b> / {len(lista_file)}"

            if parent_widget:
                QMessageBox.information(parent_widget, "Creazione File Completata", msg)

            logging.info(f"[MAKE-FILES] Creati {file_creati} file nella cartella '{cartella_path}'.")

        except Exception as err:
            logging.error(f"[MAKE-FILES] Errore durante la creazione dei file: {err}")
            if parent_widget:
                QMessageBox.critical(parent_widget, "Errore Creazione File", f"Impossibile creare i file su disco:\n{err}")

