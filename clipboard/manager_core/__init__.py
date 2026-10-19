"""
PADAS CLIPBOARD MANAGER - ORCHESTRATORE PRINCIPALE
Unisce tutti i mixin modulari del pacchetto manager_core assicurando il corretto ordine MRO.
"""

from .base_manager import PadasClipboardManagerBase
from .menu_toolbar_events import MenuToolbarEventsMixin
from .clipboard_listener import ClipboardListenerMixin
from .slot_operations import SlotOperationsMixin
from .lock_clear_operations import LockClearOperationsMixin
from .table_keyboard_controller import TableKeyboardControllerMixin


class PadasClipboardManager(
    TableKeyboardControllerMixin,
    LockClearOperationsMixin,
    SlotOperationsMixin,
    MenuToolbarEventsMixin,
    ClipboardListenerMixin,
    PadasClipboardManagerBase
):
    """Controller principale dell'applicazione assemblato tramite pattern Mixin."""
    pass


__all__ = ["PadasClipboardManager"]