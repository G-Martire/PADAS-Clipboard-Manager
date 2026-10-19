"""
PADAS CLIPBOARD MANAGER - KEYBOARD MAP ORCHESTRATOR
Unisce tutti i mixin modulari del pacchetto keyboard_map_core.
"""

from PyQt6.QtWidgets import QFrame
from .map_core import KeyboardMapCoreMixin
from .map_ui import KeyboardMapUIMixin
from .map_actions import KeyboardMapActionsMixin
from .map_multipaste import KeyboardMapMultipasteMixin


class KeyboardMapWidget(
    QFrame,
    KeyboardMapCoreMixin,
    KeyboardMapUIMixin,
    KeyboardMapActionsMixin,
    KeyboardMapMultipasteMixin
):
    """Pannello laterale contenente la griglia della tastiera virtuale con supporto a layout, tasti custom e Drag & Drop."""

    def __init__(self, parent=None, config_path=None):
        super().__init__(parent)
        self._inizializza_core_mappa(config_path)
        self.init_ui()


__all__ = ["KeyboardMapWidget"]

