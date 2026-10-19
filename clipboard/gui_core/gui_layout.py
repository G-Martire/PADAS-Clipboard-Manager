"""
PADAS CLIPBOARD MANAGER - GUI LAYOUT MIXIN
Gestisce la costruzione della finestra principale, la barra del titolo personalizzata e i contenitori di layout.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizeGrip
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class GUILayoutMixin:
    """Mixin per la costruzione della struttura dei layout della GUI."""

    def init_ui(self):
        self.setWindowTitle("PADAS DevStudio - Clipboard Memory Manager (PyQt6)")
        self.resize(1020, 500)
        self.setMinimumSize(700, 350)
        
        # Stili standard PyQt6 sicuri per finestre frameless minimizzabili
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowMinimizeButtonHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Contenitore principale
        main_frame = QFrame(self)
        main_frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(6, 6, 6, 6)
        frame_layout.setSpacing(6)

        # ------------------------------------------------------------------
        # RIGA 1: BARRA DEL TITOLO PERSONALIZZATA
        # ------------------------------------------------------------------
        self.title_bar_container = QWidget(self)
        title_bar = QHBoxLayout(self.title_bar_container)
        title_bar.setContentsMargins(10, 4, 4, 4)

        lbl_title = QLabel("PADAS DevStudio - Clipboard Memory Manager", self)
        lbl_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        title_bar.addWidget(lbl_title)
        title_bar.addStretch()

        self.btn_nascondi = QPushButton("⬇", self)
        self.btn_nascondi.setToolTip("Nascondi in background (Richiamabile con Shift + Alt + S)")
        self.btn_nascondi.setFixedSize(30, 24)

        self.btn_riduci = QPushButton("—", self)
        self.btn_riduci.setToolTip("Riduci a icona sulla barra delle applicazioni")
        self.btn_riduci.setFixedSize(30, 24)

        self.btn_ingrandisci = QPushButton("🗖", self)
        self.btn_ingrandisci.setToolTip("Ingrandisci / Ripristina dimensione")
        self.btn_ingrandisci.setFixedSize(30, 24)

        self.btn_chiudi = QPushButton("✕", self)
        self.btn_chiudi.setFixedSize(30, 24)
        self.btn_chiudi.setToolTip("Chiudi l'applicazione e termina il processo")

        title_bar.addWidget(self.btn_nascondi)
        title_bar.addWidget(self.btn_riduci)
        title_bar.addWidget(self.btn_ingrandisci)
        title_bar.addWidget(self.btn_chiudi)

        frame_layout.addWidget(self.title_bar_container)

        # Inserimento dei componenti aggiunti tramite gli altri Mixin
        if hasattr(self, '_costruisci_menu_e_toolbar'):
            self._costruisci_menu_e_toolbar(frame_layout)
        
        if hasattr(self, '_costruisci_tabella_e_mappa'):
            self._costruisci_tabella_e_mappa(frame_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        size_grip = QSizeGrip(self)
        bottom_layout.addWidget(size_grip)
        frame_layout.addLayout(bottom_layout)

        layout.addWidget(main_frame)

