"""
PADAS CLIPBOARD MANAGER - KEYBOARD MAP UI
Gestisce la costruzione dell'interfaccia grafica e dei layout dei tasti per KeyboardMapWidget.
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .virtual_key import VirtualKeyWidget


class KeyboardMapUIMixin:
    """Mixin per la costruzione dell'interfaccia grafica della mappa tastiera."""

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            KeyboardMapWidget {
                background-color: #f1f8e9;
                border: 1px solid #a5d6a7;
                border-radius: 6px;
            }
        """)

        if self.layout():
            QWidget().setLayout(self.layout())

        self.tasti_map.clear()
        self.righe_layouts = []

        layout_principale = QVBoxLayout(self)
        layout_principale.setContentsMargins(8, 8, 8, 8)
        layout_principale.setSpacing(4)

        header_layout = QHBoxLayout()
        lbl_titolo = QLabel("Mappa Slot Tastiera", self)
        lbl_titolo.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl_titolo.setStyleSheet("color: #1b4332;")
        header_layout.addWidget(lbl_titolo)
        header_layout.addStretch()

        btn_multi_paste = QPushButton("📋", self)
        btn_multi_paste.setFixedSize(24, 22)
        btn_multi_paste.setToolTip("Configura e riattiva l'anteprima Incollo Multiplo (Shift + Alt + E)")
        btn_multi_paste.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_multi_paste.setStyleSheet("""
            QPushButton {
                background-color: #c8e6c9;
                border: 1px solid #a5d6a7;
                border-radius: 3px;
                color: #1b4332;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a5d6a7;
            }
        """)
        btn_multi_paste.clicked.connect(self.apri_configurazione_incollo_multiplo)
        header_layout.addWidget(btn_multi_paste)

        self.btn_edit_mode = QPushButton("🖐️", self)
        self.btn_edit_mode.setFixedSize(24, 22)
        self.btn_edit_mode.setCheckable(True)
        self.btn_edit_mode.setChecked(self.edit_mode)
        self.btn_edit_mode.setToolTip("Attiva/Disattiva modalità spostamento tasti (Drag & Drop)")
        self.btn_edit_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self._aggiorna_stile_btn_edit()
        self.btn_edit_mode.clicked.connect(self.toggle_edit_mode)
        header_layout.addWidget(self.btn_edit_mode)

        btn_config = QPushButton("⚙", self)
        btn_config.setFixedSize(24, 22)
        btn_config.setToolTip("Personalizza layout di base e aggiungi tasti extra...")
        btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_config.setStyleSheet("""
            QPushButton {
                background-color: #c8e6c9;
                border: 1px solid #a5d6a7;
                border-radius: 3px;
                color: #1b4332;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a5d6a7;
            }
        """)
        btn_config.clicked.connect(self.apri_dialogo_configurazione)
        header_layout.addWidget(btn_config)

        layout_principale.addLayout(header_layout)

        matrice_layout = self._costruisci_layout_corrente()
        rientri_righe = [0, 12, 20, 32, 0]

        for row_idx, row_keys in enumerate(matrice_layout):
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(2)

            indent_px = rientri_righe[row_idx] if row_idx < len(rientri_righe) else 0
            if indent_px > 0:
                row_layout.addSpacing(indent_px)

            for key in row_keys:
                btn_key = VirtualKeyWidget(key_label=key, slot_id=key, parent=self)
                btn_key.setFixedSize(32, 32)
                btn_key.set_edit_mode(self.edit_mode)
                btn_key.key_clicked.connect(self.slot_selected.emit)
                btn_key.key_swapped.connect(self._scambia_posizioni_tasti)
                
                row_layout.addWidget(btn_key)
                self.tasti_map[key.lower()] = btn_key

            row_layout.addStretch()
            layout_principale.addLayout(row_layout)
            self.righe_layouts.append(row_layout)

        layout_principale.addStretch()

    def _aggiorna_stile_btn_edit(self):
        if self.edit_mode:
            self.btn_edit_mode.setStyleSheet("""
                QPushButton {
                    background-color: #fff59d;
                    border: 1px solid #fbc02d;
                    border-radius: 3px;
                    color: #f57f17;
                    font-weight: bold;
                }
            """)
        else:
            self.btn_edit_mode.setStyleSheet("""
                QPushButton {
                    background-color: #c8e6c9;
                    border: 1px solid #a5d6a7;
                    border-radius: 3px;
                    color: #1b4332;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #a5d6a7;
                }
            """)

