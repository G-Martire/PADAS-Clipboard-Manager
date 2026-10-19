"""
PADAS CLIPBOARD MANAGER - SIGNALS
Definizione dei segnali PyQt6 per la gestione della clipboard.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class ClipboardSignals(QObject):
    """Classe contenente i segnali per la comunicazione asincrona e thread-safe dell'applicazione."""
    show_gui = pyqtSignal()
    trigger_copy = pyqtSignal()
    trigger_paste = pyqtSignal()
    trigger_from_clipboard = pyqtSignal()
    trigger_copy_format = pyqtSignal()
    trigger_apply_preset = pyqtSignal()
    trigger_paste_slot = pyqtSignal(str)            # Incollo diretto dallo slot
    trigger_multi_paste_slot = pyqtSignal(str, str) # Incollo multiplo per coordinate (Shift + Alt + R)
    trigger_save_slot = pyqtSignal(str)             # Salvataggio diretto nello slot (Shift + Alt + Z)
    trigger_split_save_slot = pyqtSignal(str, str)  # Split & Save (Shift + Alt + A)
    trigger_create_files_slot = pyqtSignal(str, str)# Creazione File/Cartelle (Shift + Alt + M)
    trigger_drive_image_upload = pyqtSignal()       # Upload Immagine su Google Drive & Copia Link (Shift + Alt + E)
    trigger_clear_slot = pyqtSignal(str)            # Cancellazione (Shift + Alt + W)
    trigger_toggle_lock = pyqtSignal(str)           # Blocco/sblocco slot (Shift + Alt + Q)


# Istanza globale dei segnali da condividere tra i moduli
signals = ClipboardSignals()

