"""
PADAS CLIPBOARD MANAGER - VIRTUAL KEY WIDGET
Widget che rappresenta un singolo tasto virtuale sulla mappa con supporto al Drag & Drop per lo spostamento.
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QFont


class VirtualKeyWidget(QPushButton):
    """Widget che rappresenta un singolo tasto virtuale sulla mappa con supporto al Drag & Drop per lo spostamento."""
    
    key_clicked = pyqtSignal(str)
    key_swapped = pyqtSignal(str, str)

    def __init__(self, key_label: str, slot_id: str = None, parent=None):
        super().__init__(parent)
        self.key_label = key_label
        self.slot_id = (slot_id or key_label).lower()
        self.is_occupied = False
        self.is_locked = False
        self.edit_mode = False

        self.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._on_clicked)
        
        self.setAcceptDrops(True)
        self.aggiorna_stato(occupied=False, locked=False)

    def set_edit_mode(self, enabled: bool):
        self.edit_mode = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.aggiorna_stato(self.is_occupied, self.is_locked)

    def _on_clicked(self):
        if not self.edit_mode:
            self.key_clicked.emit(self.slot_id)

    def mouseMoveEvent(self, event):
        if self.edit_mode and event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.slot_id)
            drag.setMimeData(mime_data)
            drag.exec(Qt.DropAction.MoveAction)
        else:
            super().mouseMoveEvent(event)

    def dragEnterEvent(self, event):
        if self.edit_mode and event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if self.edit_mode and event.mimeData().hasText():
            slot_sorgente = event.mimeData().text()
            slot_destinazione = self.slot_id
            if slot_sorgente != slot_destinazione:
                self.key_swapped.emit(slot_sorgente, slot_destinazione)
            event.acceptProposedAction()

    def aggiorna_stato(self, occupied: bool = False, locked: bool = False):
        self.is_occupied = occupied
        self.is_locked = locked

        label_testo = self.key_label.upper()
        if self.edit_mode:
            bg_color = "#fff59d"
            text_color = "#f57f17"
            border_color = "#fbc02d"
        elif self.is_locked:
            label_testo = f"🔒{label_testo}"
            bg_color = "#e57373"
            text_color = "#ffffff"
            border_color = "#c62828"
        elif self.is_occupied:
            bg_color = "#81c784"
            text_color = "#1b4332"
            border_color = "#2e7d32"
        else:
            bg_color = "#e8f5e9"
            text_color = "#2e7d32"
            border_color = "#a5d6a7"

        self.setText(label_testo)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 2px;
            }}
            QPushButton:hover {{
                border: 2px solid #1b4332;
            }}
        """)

