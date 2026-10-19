"""
PADAS CLIPBOARD MANAGER - PASTE ACTIONS
Logica di incollo diretto da singolo slot verso la clipboard e invio dei tasti di sistema.
"""

import time
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl, QMimeData
from PyQt6.QtGui import QImage
from .selective_format import SelectiveFormatManager


class PasteActionsManager:
    """Gestisce l'incollo diretto da singolo slot tramite composizione."""

    def __init__(self, manager):
        self.manager = manager  # Riceve il riferimento al Manager principale

    def incolla_da_slot(self, tasto_slot: str, memoria: list, rilascia_modificatori_fn):
        """Trova lo slot ed esegue l'incollo diretto."""
        slot_clean = tasto_slot.strip().lower()
        item = next((e for e in memoria if e.get("slot") == slot_clean), None)

        if not item:
            logging.warning(f"[LOG-PASTE] Slot '{slot_clean.upper()}' VUOTO o non trovato in memoria!")
            return

        logging.info(f"[LOG-PASTE] Caricamento dati dello slot '{slot_clean.upper()}' (ID {item.get('id')}, {item['tipo']}) nella clipboard...")
        clipboard = QApplication.clipboard()

        if item.get("dato") == SelectiveFormatManager.SEGNAPOSTO_SOLO_STILE:
            mime = QMimeData()
            mime.setHtml(item.get("html", ""))
            clipboard.setMimeData(mime)

        elif item["tipo"] == "Immagine":
            img_path = Path(item["dato"])
            if img_path.exists():
                image = QImage(str(item["dato"]))
                clipboard.setImage(image)
            else:
                clipboard.setText(item["dato"])

        elif item["tipo"] == "File/Cartelle":
            paths = [p.strip() for p in item["dato"].split(";") if p.strip()]
            urls = [QUrl.fromLocalFile(p) for p in paths]
            
            mime = QMimeData()
            mime.setUrls(urls)
            mime.setText("\n".join(paths))
            mime.setData("Preferred DropEffect", b"\x05\x00\x00\x00")
            
            dropfiles_header = b"\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00"
            paths_encoded = "\x00".join(paths).encode("utf-16le") + b"\x00\x00\x00\x00"
            hdrop_bytes = dropfiles_header + paths_encoded
            
            mime.setData("application/x-qt-windows-mime;value=\"FileNameW\"", paths_encoded)
            mime.setData("application/x-qt-windows-mime;value=\"FileGroupDescriptorW\"", hdrop_bytes)
            
            clipboard.setMimeData(mime)

        else:
            mime = QMimeData()
            if item.get("html"):
                mime.setHtml(item["html"])
            if item.get("dato"):
                mime.setText(item["dato"])
            clipboard.setMimeData(mime)

        logging.info("[LOG-PASTE] Rilascio preventivo modificatori e invio comando d'incollo diretto di sistema...")
        rilascia_modificatori_fn()
        time.sleep(0.08)

        import keyboard
        keyboard.send('ctrl+v')
        logging.info(f"[LOG-PASTE] Operazione incolla completata per lo Slot '{slot_clean.upper()}'!")

