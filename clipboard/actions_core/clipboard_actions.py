"""
PADAS CLIPBOARD MANAGER - CLIPBOARD ACTIONS
Gestione dell'estrazione dati di base dalla clipboard di sistema e della cattura massiva.
"""

import time
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication

MEDIA_DIR = Path("padas_clipboard_media")
MEDIA_DIR.mkdir(exist_ok=True)


class ClipboardActionsManager:
    """Gestisce l'estrazione dati dalla clipboard di sistema (testi, immagini, file) tramite composizione."""

    def __init__(self, manager):
        self.manager = manager  # Riceve il riferimento al Manager principale

    def estrai_e_salva_dati(self, tasto_slot: str, memoria: list, refresh_callback):
        """Estrae i dati presenti nella clipboard e li aggiunge come scheda con ID alla memoria."""
        logging.info(f"[LOG-ACTION] Estrazione dati dalla clipboard per lo Slot '{tasto_slot.upper()}'...")
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

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

    def estrai_e_salva_massivo(self, elementi_massivi: list, refresh_callback):
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

    @classmethod
    def upload_immagine_drive_e_copia_link(cls, parent_widget=None):
        """
        Estrae l'immagine presente negli appunti di sistema, la carica su Google Drive via API,
        sostituisce la clipboard con il link web ed esegue l'incollo automatico (Ctrl + V).
        """
        import time
        import logging
        import winsound
        import keyboard
        from pathlib import Path
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import Qt
        from .drive_uploader import GoogleDriveService

        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        # 1. Verifica che negli appunti ci sia un'immagine
        if not mime_data.hasImage():
            logging.warning("[DRIVE-UPLOAD] Nessuna immagine rilevata negli appunti di sistema.")
            try:
                winsound.Beep(300, 250)
            except Exception:
                pass
            if parent_widget:
                dlg = QMessageBox(parent_widget)
                dlg.setIcon(QMessageBox.Icon.Warning)
                dlg.setWindowTitle("Nessuna Immagine negli Appunti")
                dlg.setText("<b>Impossibile eseguire l'upload su Google Drive!</b><br><br>"
                             "Negli appunti di sistema non è presente alcuna immagine.<br>"
                             "Cattura prima una schermata con <code>Shift + Win + S</code> e poi riprova.")
                dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
                dlg.exec()
            return

        try:
            # 2. Salvataggio temporaneo dell'immagine dagli appunti su disco
            q_image = clipboard.image()
            temp_dir = Path("padas_clipboard_media")
            temp_dir.mkdir(exist_ok=True)
            temp_file = temp_dir / f"drive_upload_{int(time.time()*1000)}.png"
            q_image.save(str(temp_file), "PNG")

            logging.info(f"[DRIVE-UPLOAD] Immagine salvata temporaneamente in '{temp_file}'. Avvio upload...")

            # 3. Upload su Google Drive e recupero del link condivisibile
            link_web = GoogleDriveService.carica_immagine_e_ottieni_link(temp_file)

            # 4. Sostituzione degli appunti con il link di Google Drive
            clipboard.setText(link_web)
            logging.info(f"[DRIVE-UPLOAD] Link Google Drive copiato negli appunti: {link_web}")

            # 5. Rilascio sicuro dei tasti modificatori e Incollo Automatico (Ctrl + V)
            tasti_mod = ['shift', 'left shift', 'right shift', 'alt', 'left alt', 'right alt', 'alt gr', 'ctrl', 'left ctrl', 'right ctrl']
            for k in tasti_mod:
                try:
                    if keyboard.is_pressed(k):
                        keyboard.release(k)
                except Exception:
                    pass

            time.sleep(0.05)
            keyboard.send('ctrl+v')

            try:
                winsound.Beep(1200, 150)
            except Exception:
                pass

        except FileNotFoundError as fnf_err:
            logging.error(f"[DRIVE-UPLOAD] Errore credenziali: {fnf_err}")
            if parent_widget:
                dlg = QMessageBox(parent_widget)
                dlg.setIcon(QMessageBox.Icon.Critical)
                dlg.setWindowTitle("Credenziali Google Mancanti")
                dlg.setText(f"<b>File credenziali mancante!</b><br><br>{fnf_err}")
                dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
                dlg.exec()
        except Exception as err:
            logging.error(f"[DRIVE-UPLOAD] Errore durante l'upload dell'immagine su Drive: {err}")
            if parent_widget:
                dlg = QMessageBox(parent_widget)
                dlg.setIcon(QMessageBox.Icon.Critical)
                dlg.setWindowTitle("Errore Upload Google Drive")
                dlg.setText(f"Si è verificato un errore durante l'upload dell'immagine su Google Drive:\n\n{err}")
                dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
                dlg.exec()


