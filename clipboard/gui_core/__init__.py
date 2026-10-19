"""
PADAS CLIPBOARD MANAGER - GUI CORE ORCHESTRATOR
Unisce tutti i mixin modulari del pacchetto gui_core nella classe finale ClipboardGUI.
"""

from PyQt6.QtWidgets import QWidget
from .gui_core import GUICoreMixin
from .gui_layout import GUILayoutMixin
from .gui_menus import GUIMenusMixin
from .gui_table import GUITableMixin
from .gui_dialogs import GUIDialogsMixin


class ClipboardGUI(
    GUICoreMixin,
    GUILayoutMixin,
    GUIMenusMixin,
    GUITableMixin,
    GUIDialogsMixin,
    QWidget
):
    """Finestra principale dell'applicazione assemblata tramite architettura a componenti (Mixin)."""

    def __init__(self):
        super().__init__()
        self._inizializza_core_gui()
        self.init_ui()


__all__ = ["ClipboardGUI"]
