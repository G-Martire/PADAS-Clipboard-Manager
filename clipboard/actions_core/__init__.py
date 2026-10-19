"""
PADAS CLIPBOARD MANAGER - ACTIONS CORE
Manager principale per la gestione delle azioni, basato sul pattern a COMPOSIZIONE.
Funge anche da Facade di compatibilità per il vecchio stile d'importazione.
"""

from pathlib import Path
from .text_splitter import TextSplitterHelper
from .keyboard_grid import KeyboardGridHelper
from .clipboard_actions import ClipboardActionsManager
from .split_save_actions import SplitSaveActionsManager
from .selective_format import SelectiveFormatManager
from .paste_actions import PasteActionsManager
from .coordinate_utils import CoordinateUtils
from .multi_paste_actions import MultiPasteActionsManager
from .file_maker_actions import FileMakerActionsManager

MEDIA_DIR = Path("padas_clipboard_media")
MEDIA_DIR.mkdir(exist_ok=True)


class ClipboardActionsCompatibilityFacade:
    """
    Classe di compatibilità (Facade) che mappa i vecchi metodi statici o diretti 
    di ClipboardActions verso i nuovi manager modulari interni.
    """
    
    # Istanziamo i manager necessari per delegare le chiamate
    _paste_mgr = PasteActionsManager(None)
    _clipboard_mgr = ClipboardActionsManager(None)
    _split_save_mgr = SplitSaveActionsManager(None)
    _selective_mgr = SelectiveFormatManager(None)
    _file_maker_mgr = FileMakerActionsManager(None)

    @classmethod
    def incolla_da_slot(cls, tasto_slot, memoria, rilascia_modificatori_fn):
        return cls._paste_mgr.incolla_da_slot(tasto_slot, memoria, rilascia_modificatori_fn)

    @classmethod
    def estrai_e_salva_dati(cls, *args, **kwargs):
        return cls._clipboard_mgr.estrai_e_salva_dati(*args, **kwargs)

    @classmethod
    def split_and_save_dati(cls, *args, **kwargs):
        return cls._split_save_mgr.split_and_save_dati(*args, **kwargs)

    @classmethod
    def estrai_formato_selettivo(cls, *args, **kwargs):
        return cls._selective_mgr.estrai_formato_selettivo(*args, **kwargs)

    @classmethod
    def crea_file_e_cartelle(cls, *args, **kwargs):
        return cls._file_maker_mgr.crea_file_e_cartelle(*args, **kwargs)

    @classmethod
    def upload_immagine_drive_e_copia_link(cls, *args, **kwargs):
        return cls._clipboard_mgr.upload_immagine_drive_e_copia_link(*args, **kwargs)


# Alias di compatibilità: chiunque importi ClipboardActions userà questa Facade trasparente
ClipboardActions = ClipboardActionsCompatibilityFacade


class ActionsManager:
    """Manager principale che compone tutti i moduli operativi delle azioni e della clipboard."""

    def __init__(self):
        super().__init__()
        # Inizializzazione dei moduli figli tramite composizione (passando self come riferimento)
        self.text_splitter = TextSplitterHelper()
        self.keyboard_grid = KeyboardGridHelper()
        self.clipboard_actions = ClipboardActionsManager(self)
        self.split_save_actions = SplitSaveActionsManager(self)
        self.selective_format = SelectiveFormatManager(self)
        self.paste_actions = PasteActionsManager(self)
        self.coordinate_utils = CoordinateUtils(self)
        self.multi_paste_actions = MultiPasteActionsManager(self)
        self.file_maker_actions = FileMakerActionsManager(self)

