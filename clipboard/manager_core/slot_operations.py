"""
PADAS CLIPBOARD MANAGER - SLOT OPERATIONS MIXIN
Gestisce le operazioni di salvataggio, incollo, formati selettivi, preset e creazione file/cartelle sugli slot.
"""

import time
import logging
import winsound
from PyQt6.QtWidgets import QMessageBox
from ..actions_core import ClipboardActions
from ..dialogs_core import FormatoFilterDialog


class SlotOperationsMixin:
    """Mixin per la gestione delle operazioni sugli slot e formati."""

    def esegui_salvataggio_da_segnale(self, tasto_slot: str):
        """Riceve lo slot ed esegue il salvataggio verificando che lo slot non sia BLOCCATO."""
        logging.info(f"[LOG-MANAGER] Ricevuto segnale Thread-Safe per SALVATAGGIO nello Slot '{tasto_slot.upper()}'.")
        if tasto_slot:
            slot_clean = tasto_slot.strip().lower()
            item_esistente = next((e for e in self.memoria if e.get("slot") == slot_clean), None)

            if item_esistente and item_esistente.get("bloccato", False):
                logging.warning(f"[LOG-MANAGER] Salvataggio BLOCCATO: Lo slot '{slot_clean.upper()}' è protetto (🔒)!")
                try:
                    winsound.Beep(300, 250)
                except Exception:
                    pass
                QMessageBox.warning(
                    self,
                    "Slot Bloccato",
                    f"Lo Slot '{slot_clean.upper()}' è BLOCCATO (🔒)!\n\n"
                    f"Sbloccalo prima con la sequenza 'Shift + Alt + Q' e poi lo slot '{slot_clean.upper()}' per poterlo sovrascrivere."
                )
                return

            self._blocco_cattura_massiva = True
            try:
                ClipboardActions.estrai_e_salva_dati(tasto_slot, self.memoria, self._refresh)
                self._notifica_salvataggio()
            finally:
                time.sleep(0.05)
                self._blocco_cattura_massiva = False

    def esegui_split_save_da_segnale(self, slot_inizio: str, param2: str):
        """Riceve i parametri ed esegue l'operazione di Split & Save (Copia Multipla)."""
        logging.info(f"[LOG-MANAGER] Ricevuto segnale per SPLIT & SAVE da Slot '{slot_inizio.upper()}', Param2 '{param2.upper()}'.")
        if slot_inizio:
            layout_matrice = []
            if hasattr(self, "keyboard_map") and self.keyboard_map:
                layout_matrice = self.keyboard_map._costruisci_layout_corrente()

            config_split = getattr(self, "config_split_save", {})

            self._blocco_cattura_massiva = True
            try:
                ClipboardActions.split_and_save_dati(
                    slot_inizio=slot_inizio,
                    param2=param2,
                    memoria=self.memoria,
                    elementi_massivi=self.elementi_massivi,
                    layout_matrice=layout_matrice,
                    config_split=config_split,
                    refresh_callback=self._refresh,
                    parent_widget=self
                )
            finally:
                time.sleep(0.05)
                self._blocco_cattura_massiva = False

    def esegui_creazione_file_da_segnale(self, slot_inizio: str, param2: str):
        """Riceve i parametri ed esegue la Creazione File/Cartelle (Shift + Alt + M)."""
        logging.info(f"[LOG-MANAGER] Ricevuto segnale per CREAZIONE FILE da Slot '{slot_inizio.upper()}', Param2 '{param2.upper()}'.")
        if slot_inizio:
            layout_matrice = []
            if hasattr(self, "keyboard_map") and self.keyboard_map:
                layout_matrice = self.keyboard_map._costruisci_layout_corrente()

            self._blocco_cattura_massiva = True
            try:
                ClipboardActions.crea_file_e_cartelle(
                    slot_inizio=slot_inizio,
                    param2=param2,
                    memoria=self.memoria,
                    layout_matrice=layout_matrice,
                    parent_widget=self
                )
            finally:
                time.sleep(0.05)
                self._blocco_cattura_massiva = False

    def esegui_incollo_da_segnale(self, tasto_slot: str):
        """Riceve lo slot via segnale PyQt6 ed esegue l'incollo."""
        logging.info(f"[LOG-MANAGER] Ricevuto segnale Thread-Safe per INCOLLO dallo Slot '{tasto_slot.upper()}'.")
        if tasto_slot:
            slot_clean = tasto_slot.strip().lower()
            slot_trovato = any(item.get("slot") == slot_clean for item in self.memoria)
            
            if slot_trovato:
                self._blocco_cattura_massiva = True
                try:
                    ClipboardActions.incolla_da_slot(slot_clean, self.memoria, self.hotkey_mgr.rilascia_tasti_modifica)
                finally:
                    time.sleep(0.05)
                    self._blocco_cattura_massiva = False
            else:
                logging.warning(f"[LOG-MANAGER] Lo slot '{tasto_slot.upper()}' risulta VUOTO o non trovato!")

    def salva_da_clipboard_sistema(self):
        """Scorciatoia Shift + Alt + X (Salva da Clipboard)."""
        tasto_slot = self.hotkey_mgr.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
        if tasto_slot:
            self._blocco_cattura_massiva = True
            try:
                ClipboardActions.estrai_e_salva_dati(tasto_slot, self.memoria, self._refresh)
                self._notifica_salvataggio()
            finally:
                time.sleep(0.05)
                self._blocco_cattura_massiva = False

    def copia_formato_selettivo(self):
        """Shift + Alt + F: Copia Formato Selettivo."""
        dlg = FormatoFilterDialog(config_smart={"auto_smart": getattr(self, "auto_smart_attivo", True)}, parent=self)
        if dlg.exec():
            filtri = dlg.get_filtri()
            self.auto_smart_attivo = filtri.get("auto_smart", True)
            self.ultimo_filtro_usato = filtri
            
            tasto_slot = self.hotkey_mgr.cattura_singolo_tasto_invisibile()
            if tasto_slot:
                self._blocco_cattura_massiva = True
                try:
                    ClipboardActions.estrai_formato_selettivo(tasto_slot, self.memoria, filtri, self._refresh)
                    self._notifica_salvataggio()
                finally:
                    time.sleep(0.05)
                    self._blocco_cattura_massiva = False

    def applica_preset_formato(self):
        """Shift + Alt + G: Applica Preset."""
        tasto_slot = self.hotkey_mgr.cattura_singolo_tasto_invisibile()
        if tasto_slot:
            filtri_da_usare = getattr(self, "ultimo_filtro_usato", {
                "auto_smart": True, "font": True, "size": True, "bold_italic": True,
                "color": True, "bg_color": True, "borders": True, "align": True
            })
            self._blocco_cattura_massiva = True
            try:
                ClipboardActions.estrai_formato_selettivo(tasto_slot, self.memoria, filtri_da_usare, self._refresh)
                self._notifica_salvataggio()
            finally:
                time.sleep(0.05)
                self._blocco_cattura_massiva = False

    def _estrai_e_salva_massivo(self):
        """Estrae e salva nella cattura massiva."""
        ClipboardActions.estrai_e_salva_massivo(self.elementi_massivi, self._refresh)

    def esegui_incollo_multiplo_da_segnale(self, slot_inizio: str, slot_fine: str):
        """Incollo multiplo a coordinate."""
        logging.info(f"[LOG-HOTKEY] Coordinate '{slot_inizio.upper()}' -> '{slot_fine.upper()}' intercettate. Emissione segnale Thread-Safe per INCOLLO MULTIPLO.")
        
        layout_matrice = []
        if hasattr(self, "keyboard_map") and self.keyboard_map:
            layout_matrice = self.keyboard_map._costruisci_layout_corrente()

        ClipboardActions.incolla_multiplo_coordinate(
            slot_start=slot_inizio,
            slot_end=slot_fine,
            memoria=self.memoria,
            layout_matrice=layout_matrice,
            callback_release_keys=self.hotkey_mgr.rilascia_tasti_modifica,
            parent_widget=self
        )

    def esegui_upload_drive_da_segnale(self):
        """
        Riceve il segnale per l'upload dell'immagine negli appunti su Google Drive (Shift + Alt + E).
        Estrae l'immagine dalla clipboard di sistema, la carica su Drive e sostituisce la clipboard con il link web.
        """
        logging.info("[LOG-MANAGER] Ricevuto segnale Thread-Safe per UPLOAD IMMAGINE DRIVE (Shift + Alt + E)...")
        self._blocco_cattura_massiva = True
        try:
            ClipboardActions.upload_immagine_drive_e_copia_link(parent_widget=self)
        finally:
            time.sleep(0.05)
            self._blocco_cattura_massiva = False

