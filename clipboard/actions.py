"""
PADAS CLIPBOARD MANAGER - ACTIONS E MANIPOLAZIONE DATI CON LOGGER
Contiene la logica operativa per estrarre, salvare ed incollare direttamente i dati negli slot.
"""

import time
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl, QMimeData
from PyQt6.QtGui import QImage

MEDIA_DIR = Path("padas_clipboard_media")
MEDIA_DIR.mkdir(exist_ok=True)


class ClipboardActions:
    """Gestisce l'estrazione dati dalla clipboard di sistema e l'operazione di incollo diretto negli slot."""

    @staticmethod
    def estrai_e_salva_dati(tasto_slot: str, memoria: list, refresh_callback):
        """Estrae i dati presenti nella clipboard e li aggiunge come scheda con ID alla memoria."""
        logging.info(f"[LOG-ACTION] Estrazione dati dalla clipboard per lo Slot '{tasto_slot.upper()}'...")
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        # Generazione ID univoco progressivo
        nuovo_id = max([item.get("id", 0) for item in memoria], default=0) + 1
        slot_clean = tasto_slot.strip().lower()

        if mime_data.hasImage():
            image = clipboard.image()
            img_path = MEDIA_DIR / f"slot_{slot_clean}_{nuovo_id}.png"
            image.save(str(img_path), "PNG")
            path_str = str(img_path.resolve())
            nuovo_elemento = {
                "id": nuovo_id, "slot": slot_clean, "tipo": "Immagine",
                "dato": path_str, "html": "", "anteprima": path_str, "note": ""
            }
            logging.info(f"[LOG-ACTION] Immagine salvata nello slot '{slot_clean.upper()}' (ID {nuovo_id}).")

        elif mime_data.hasUrls():
            urls = [url.toLocalFile() for url in mime_data.urls()]
            path_str = "; ".join(urls)
            nuovo_elemento = {
                "id": nuovo_id, "slot": slot_clean, "tipo": "File/Cartelle",
                "dato": path_str, "html": "", "anteprima": path_str, "note": ""
            }
            logging.info(f"[LOG-ACTION] File/Cartelle salvati nello slot '{slot_clean.upper()}' (ID {nuovo_id}).")

        elif mime_data.hasHtml() or mime_data.hasText():
            testo_puro = mime_data.text() if mime_data.hasText() else ""
            html_data = mime_data.html() if mime_data.hasHtml() else ""
            tipo = "Tabella/Matrice Formattata" if ("\t" in testo_puro or "\n" in testo_puro) else "Testo"

            nuovo_elemento = {
                "id": nuovo_id, "slot": slot_clean, "tipo": tipo,
                "dato": testo_puro, "html": html_data,
                "anteprima": testo_puro.replace("\n", " ")[:50], "note": ""
            }
            logging.info(f"[LOG-ACTION] Testo/HTML salvato nello slot '{slot_clean.upper()}' (ID {nuovo_id}) -> {testo_puro[:30]}...")
        else:
            return

        memoria.append(nuovo_elemento)
        refresh_callback()

    @staticmethod
    def estrai_e_salva_massivo(elementi_massivi: list, refresh_callback):
        """Estrae i dati correnti per la modalità di cattura massiva."""
        logging.info("[LOG-ACTION] Salvo elemento nella lista Cattura Massiva...")
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            image = clipboard.image()
            img_path = MEDIA_DIR / f"massivo_{int(time.time()*1000)}.png"
            image.save(str(img_path), "PNG")
            path_str = str(img_path.resolve())
            item = {"tipo": "Immagine", "dato": path_str, "html": "", "anteprima": path_str, "note": ""}
        elif mime_data.hasUrls():
            urls = [url.toLocalFile() for url in mime_data.urls()]
            path_str = "; ".join(urls)
            item = {"tipo": "File/Cartelle", "dato": path_str, "html": "", "anteprima": path_str, "note": ""}
        elif mime_data.hasHtml() or mime_data.hasText():
            testo_puro = mime_data.text() if mime_data.hasText() else ""
            html_data = mime_data.html() if mime_data.hasHtml() else ""
            tipo = "Tabella/Matrice Formattata" if ("\t" in testo_puro or "\n" in testo_puro) else "Testo"
            item = {"tipo": tipo, "dato": testo_puro, "html": html_data, "anteprima": testo_puro.replace("\n", " ")[:50], "note": ""}
        else:
            item = {"tipo": "Testo", "dato": "", "html": "", "anteprima": "", "note": ""}

        elementi_massivi.append(item)
        refresh_callback()

    SEGNAPOSTO_SOLO_STILE = "__PADAS_STYLE_ONLY__"

    @staticmethod
    def estrai_formato_selettivo(tasto_slot: str, memoria: list, filtri: dict, refresh_callback):
        """Estrae l'HTML filtrando le proprietà. Se non si include il testo, usa il segnaposto convenzionale."""
        logging.info(f"[LOG-ACTION] Estrazione Formato Selettivo per lo Slot '{tasto_slot.upper()}'...")
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if not (mime_data.hasHtml() or mime_data.hasText()):
            logging.warning("[LOG-ACTION] Nessun formato o testo trovato nella clipboard.")
            return

        html_data = mime_data.html() if mime_data.hasHtml() else f"<span>{mime_data.text()}</span>"
        testo_puro = mime_data.text() if mime_data.hasText() else ""
        
        # Se nel filtro abbiamo disattivato il testo o vogliamo SOLO lo stile
        mantiene_testo = filtri.get("text", False) or filtri.get("font", True) or filtri.get("bold_italic", True)
        
        if not mantiene_testo:
            dato_salvato = ClipboardActions.SEGNAPOSTO_SOLO_STILE
            tipo_descr = "Solo Stile"
            anteprima_str = "[Solo Stile / Convenzione]"
        else:
            dato_salvato = testo_puro
            is_tabella = "<table>" in html_data.lower() or "\t" in testo_puro
            tipo_descr = "Stile + Tabella" if is_tabella else "Stile + Testo"
            anteprima_str = f"[{tipo_descr}] {testo_puro.replace('\n', ' ')[:40]}"

        nuovo_id = max([item.get("id", 0) for item in memoria], default=0) + 1
        slot_clean = tasto_slot.strip().lower()

        nuovo_elemento = {
            "id": nuovo_id,
            "slot": slot_clean,
            "tipo": tipo_descr,
            "dato": dato_salvato,
            "html": html_data,
            "filtri": filtri,
            "anteprima": anteprima_str,
            "note": ""
        }

        memoria.append(nuovo_elemento)
        refresh_callback()

    @staticmethod
    def incolla_da_slot(tasto_slot: str, memoria: list, rilascia_modificatori_fn):
        """Trova lo slot ed esegue l'incollo con supporto multi-formato arricchito per file, immagini e testo."""
        slot_clean = tasto_slot.strip().lower()
        item = next((e for e in memoria if e.get("slot") == slot_clean), None)

        if not item:
            logging.warning(f"[LOG-PASTE] Slot '{slot_clean.upper()}' VUOTO o non trovato in memoria!")
            return

        logging.info(f"[LOG-PASTE] Caricamento dati dello slot '{slot_clean.upper()}' (ID {item.get('id')}, {item['tipo']}) nella clipboard...")
        clipboard = QApplication.clipboard()

        # CASO 1: Convenzione SOLO STILE (Segnaposto)
        if item.get("dato") == ClipboardActions.SEGNAPOSTO_SOLO_STILE:
            mime = QMimeData()
            mime.setHtml(item.get("html", ""))
            clipboard.setMimeData(mime)

        # CASO 2: Immagini
        elif item["tipo"] == "Immagine":
            img_path = Path(item["dato"])
            if img_path.exists():
                image = QImage(str(item["dato"]))
                clipboard.setImage(image)
            else:
                clipboard.setText(item["dato"])

        # CASO 3: File / Cartelle (Multi-Payload Nativo Windows Shell + HDROP)
        elif item["tipo"] == "File/Cartelle":
            paths = [p.strip() for p in item["dato"].split(";") if p.strip()]
            urls = [QUrl.fromLocalFile(p) for p in paths]
            
            mime = QMimeData()
            mime.setUrls(urls)
            mime.setText("\n".join(paths))  # Per terminale e blocco note
            
            # 1. Flag dell'intenzione di copia (4 byte: DROPEFFECT_COPY = 1 o 5)
            mime.setData("Preferred DropEffect", b"\x05\x00\x00\x00")
            
            # 2. Struttura binaria CF_HDROP nativa di Windows (DROPFILES struct)
            # Offset a 20 bytes (pFiles = 20), fWide = TRUE (1)
            dropfiles_header = b"\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"
            paths_encoded = "\x00".join(paths).encode("utf-16le") + b"\x00\x00\x00\x00"
            hdrop_bytes = dropfiles_header + paths_encoded
            
            # Inseriamo sia il formato OLE registrato che il formato di sistema
            mime.setData("application/x-qt-windows-mime;value=\"FileNameW\"", paths_encoded)
            mime.setData("application/x-qt-windows-mime;value=\"FileGroupDescriptorW\"", hdrop_bytes)
            
            clipboard.setMimeData(mime)

        # CASO 4: Testo + Stile completo
        else:
            mime = QMimeData()
            if item.get("html"):
                mime.setHtml(item["html"])
            if item.get("dato"):
                mime.setText(item["dato"])
            clipboard.setMimeData(mime)

        logging.info("[LOG-PASTE] Rilascio preventivo modificatori e invio comando d'incollo diretto di sistema...")
        rilascia_modificatori_fn()
        time.sleep(0.08)  # Piccolo delay per garantire che Windows liberi le chiavi di modifica

        import keyboard
        keyboard.send('ctrl+v')
        logging.info(f"[LOG-PASTE] Operazione incolla completata per lo Slot '{slot_clean.upper()}'!")

    @staticmethod
    def calcola_range_coordinate(slot_start: str, slot_end: str, layout_matrice: list) -> tuple:
        """
        Calcola gli slot compresi nel rettangolo/intervallo tra slot_start e slot_end
        in base alla matrice del layout.
        Restituisce una tupla: (lista_dettagli_slot, totale_slot_area).
        """
        start_clean = slot_start.strip().lower()
        end_clean = slot_end.strip().lower()

        pos_start = None
        pos_end = None

        for r_idx, riga in enumerate(layout_matrice):
            for c_idx, val in enumerate(riga):
                v_clean = str(val).strip().lower()
                if v_clean == start_clean:
                    pos_start = (r_idx, c_idx)
                if v_clean == end_clean:
                    pos_end = (r_idx, c_idx)

        if not pos_start or not pos_end:
            if pos_start:
                return ([{"slot": start_clean, "riga": pos_start[0], "colonna": pos_start[1]}], 1)
            return ([], 0)

        r_min, r_max = min(pos_start[0], pos_end[0]), max(pos_start[0], pos_end[0])
        c_min, c_max = min(pos_start[1], pos_end[1]), max(pos_start[1], pos_end[1])

        slot_dettagli = []
        totale_area = 0

        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                if c < len(layout_matrice[r]):
                    totale_area += 1
                    slot_name = str(layout_matrice[r][c]).strip().lower()
                    slot_dettagli.append({
                        "slot": slot_name,
                        "riga": r,
                        "colonna": c
                    })

        return (slot_dettagli, totale_area)
    
    @classmethod
    def incolla_multiplo_coordinate(cls, slot_start: str, slot_end: str, memoria: list, layout_matrice: list, callback_release_keys, parent_widget=None):
        """Calcola l'intervallo di slot, cattura il focus nativo della finestra attiva, mostra l'anteprima e ripristina il focus prima dell'incollo."""
        import time
        import ctypes
        import keyboard
        from PyQt6.QtWidgets import QApplication

        user32 = ctypes.windll.user32
        hwnd_target = user32.GetForegroundWindow()

        slot_dettagli, totale_area = cls.calcola_range_coordinate(slot_start, slot_end, layout_matrice)
        
        elementi_trovati = []
        for dett in slot_dettagli:
            s_name = dett["slot"]
            item = next((e for e in memoria if e.get("slot", "").strip().lower() == s_name), None)
            if item and item.get("dato"):
                item_copy = dict(item)
                item_copy["riga"] = dett["riga"]
                item_copy["colonna"] = dett["colonna"]
                elementi_trovati.append(item_copy)

        if not elementi_trovati:
            logging.warning(f"[LOG-ACTIONS] Nessun dato trovato nell'intervallo {slot_start.upper()} -> {slot_end.upper()}")
            return

        # Recupero opzioni salvate dalla configurazione
        config_map = getattr(parent_widget, "keyboard_map", None) if parent_widget else None
        mostra_anteprima = True
        separatore_default = "\n"
        direzione_default = "orizzontale"

        if config_map and hasattr(config_map, "config"):
            mostra_anteprima = config_map.config.get("mostra_anteprima_multi_paste", True)
            separatore_default = config_map.config.get("separatore_multi_paste", "\n")
            direzione_default = config_map.config.get("direzione_multi_paste", "orizzontale")

        testo_finale = ""

        if mostra_anteprima:
            from .dialogs import MultiPasteOptionsDialog
            dlg = MultiPasteOptionsDialog(
                slot_inizio=slot_start,
                slot_fine=slot_end,
                slot_trovati=elementi_trovati,
                totali_area=totale_area,
                parent=parent_widget
            )
            
            # RIPRISTINO STATO SALVATO PRECEDENTEMENTE
            if config_map and hasattr(config_map, "config"):
                is_custom = config_map.config.get("custom_dir_attivo", False)
                struttura_salvata = config_map.config.get("struttura_personalizzata", "")
                
                dlg.chk_custom_dir.setChecked(is_custom)
                if struttura_salvata:
                    dlg.txt_custom_order.setPlainText(struttura_salvata)

            if dlg.exec():
                testo_finale = dlg.get_testo_assemblato()
                separatore_scelto = dlg.get_separatore()
                direzione_scelta = dlg.get_direzione()
                disattiva_in_futuro = dlg.deve_disattivare_anteprima()

                # SALVATAGGIO CONFIGURAZIONE COMPLETA
                if config_map and hasattr(config_map, "config"):
                    if disattiva_in_futuro:
                        config_map.config["mostra_anteprima_multi_paste"] = False
                    config_map.config["separatore_multi_paste"] = separatore_scelto
                    config_map.config["direzione_multi_paste"] = direzione_scelta
                    config_map.config["custom_dir_attivo"] = dlg.is_custom_dir_attivo()
                    config_map.config["struttura_personalizzata"] = dlg.get_struttura_personalizzata()
                    config_map._salva_configurazione()
            else:
                return
        else:
            # Incollo diretto senza pop-up
            if direzione_default == "verticale":
                elementi_trovati.sort(key=lambda x: (x.get("colonna", 0), x.get("riga", 0)))
            else:
                elementi_trovati.sort(key=lambda x: (x.get("riga", 0), x.get("colonna", 0)))

            testi = [item.get("dato", "") for item in elementi_trovati if item.get("dato")]
            testo_finale = separatore_default.join(testi)

        if testo_finale:
            callback_release_keys()
            QApplication.clipboard().setText(testo_finale)

            if hwnd_target:
                user32.SetForegroundWindow(hwnd_target)
                time.sleep(0.1)

            keyboard.send('ctrl+v')
            logging.info(f"[LOG-ACTIONS] Incollo multiplo eseguito per l'intervallo {slot_start.upper()} -> {slot_end.upper()}")

            
    