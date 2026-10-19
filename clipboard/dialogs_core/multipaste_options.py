"""
PADAS CLIPBOARD MANAGER - DIALOGS CORE
Dialogo avanzato di anteprima e configurazione per l'incollo multiplo a coordinate (Interfaccia UI).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QLineEdit, QTextEdit, QPushButton, QDialogButtonBox, QGroupBox, QCheckBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from .matrix_preview import MatrixPreviewWidget
from .multipaste_logic import MultiPasteLogicMixin


class MultiPasteOptionsDialog(QDialog, MultiPasteLogicMixin):
    """Dialogo avanzato di anteprima e configurazione per l'incollo multiplo a coordinate."""

    def __init__(self, slot_inizio: str, slot_fine: str, slot_trovati: list, totali_area: int, parent=None):
        super().__init__(parent)
        self.slot_inizio = slot_inizio.upper()
        self.slot_fine = slot_fine.upper()
        self.slot_trovati = slot_trovati
        self.totali_area = totali_area

        self.setWindowTitle(f"Incollo Multiplo ({self.slot_inizio} ➔ {self.slot_fine})")
        self.resize(560, 640)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 1. INTESTAZIONE DETTAGLIATA
        lbl_coord = QLabel(f"<b>COORDINATE SELEZIONATE:</b> da <b>{self.slot_inizio}</b> fino a <b>{self.slot_fine}</b> ({self.totali_area} slot totali area)")
        lbl_pieni = QLabel(f"<b>SLOT PIENI / INDIVIDUATI:</b> {len(self.slot_trovati)} slot con contenuto")
        font_info = QFont("Segoe UI", 9)
        lbl_coord.setFont(font_info)
        lbl_pieni.setFont(font_info)
        layout.addWidget(lbl_coord)
        layout.addWidget(lbl_pieni)

        # 2. SEZIONE TIPOLOGIA INCOLLAGGIO
        grp_dir = QGroupBox("TIPOLOGIA INCOLLAGGIO")
        layout_dir_main = QHBoxLayout(grp_dir)

        layout_dir_options = QVBoxLayout()
        self.btn_grp_dir = QButtonGroup(self)

        self.rad_oriz = QRadioButton("↔️ Orizzontale (per Righe)")
        self.rad_vert = QRadioButton("↕️ Verticale (per Colonne)")
        self.rad_oriz.setChecked(True)

        self.btn_grp_dir.addButton(self.rad_oriz, 1)
        self.btn_grp_dir.addButton(self.rad_vert, 2)

        layout_dir_options.addWidget(self.rad_oriz)
        layout_dir_options.addWidget(self.rad_vert)

        self.chk_custom_dir = QCheckBox("🔀 Personalizzate e poi vert. / oriz.")
        layout_dir_options.addWidget(self.chk_custom_dir)

        layout_custom_hdr = QHBoxLayout()
        lbl_custom_hint = QLabel("Struttura Personalizzata (Testo tra \" \"):")
        lbl_custom_hint.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        btn_add_slots = QPushButton("📥 Inserisci {SLOTS}")
        btn_add_slots.setFixedHeight(20)
        btn_add_slots.setFont(QFont("Segoe UI", 8))
        btn_add_slots.setToolTip("Inserisce il segnaposto {SLOTS} nel punto di inserimento")
        btn_add_slots.clicked.connect(self._inserisci_segnaposto_slots)
        layout_custom_hdr.addWidget(lbl_custom_hint)
        layout_custom_hdr.addStretch()
        layout_custom_hdr.addWidget(btn_add_slots)
        layout_dir_options.addLayout(layout_custom_hdr)

        self.txt_custom_order = QTextEdit()
        self.txt_custom_order.setFixedHeight(85)
        self.txt_custom_order.setPlaceholderText('Es:\n"Gentile cliente,"\n{SLOTS}\n"Cordiali saluti"')
        self.txt_custom_order.setEnabled(False)
        layout_dir_options.addWidget(self.txt_custom_order)

        layout_dir_main.addLayout(layout_dir_options)

        self.preview_matrix_widget = MatrixPreviewWidget(self)
        layout_dir_main.addWidget(self.preview_matrix_widget)

        layout.addWidget(grp_dir)

        # 3. SEZIONE SEPARATORE INCOLLAGGIO
        grp_sep = QGroupBox("SEPARATORE INCOLLAGGIO")
        layout_sep_main = QVBoxLayout(grp_sep)

        layout_sep_radios = QHBoxLayout()
        self.btn_grp_sep = QButtonGroup(self)
        self.rad_newline = QRadioButton("A capo (\\n)")
        self.rad_virgola = QRadioButton("Virgola (,)")
        self.rad_tab = QRadioButton("Tab")
        self.rad_spazio = QRadioButton("Spazio")
        self.rad_custom_sep = QRadioButton("Personalizzato")

        self.rad_newline.setChecked(True)

        self.btn_grp_sep.addButton(self.rad_newline, 1)
        self.btn_grp_sep.addButton(self.rad_virgola, 2)
        self.btn_grp_sep.addButton(self.rad_tab, 3)
        self.btn_grp_sep.addButton(self.rad_spazio, 4)
        self.btn_grp_sep.addButton(self.rad_custom_sep, 5)

        layout_sep_radios.addWidget(self.rad_newline)
        layout_sep_radios.addWidget(self.rad_virgola)
        layout_sep_radios.addWidget(self.rad_tab)
        layout_sep_radios.addWidget(self.rad_spazio)
        layout_sep_radios.addWidget(self.rad_custom_sep)
        layout_sep_main.addLayout(layout_sep_radios)

        self.txt_custom_sep = QLineEdit()
        self.txt_custom_sep.setPlaceholderText("Inserisci separatore personalizzato (es: - o |)")
        layout_sep_main.addWidget(self.txt_custom_sep)

        layout.addWidget(grp_sep)

        lbl_preview = QLabel("ANTEPRIMA:")
        lbl_preview.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        layout.addWidget(lbl_preview)

        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        self.txt_preview.setStyleSheet("background-color: #f1f8e9; color: #1b4332; font-size: 9pt;")
        layout.addWidget(self.txt_preview)

        self.chk_skip_preview = QCheckBox("Non mostrare più l'anteprima (Incolla subito in futuro)")
        self.chk_skip_preview.setFont(QFont("Segoe UI", 8))
        layout.addWidget(self.chk_skip_preview)

        self.btn_grp_dir.idClicked.connect(self._aggiorna_anteprima)
        self.chk_custom_dir.toggled.connect(self._on_custom_dir_toggled)
        self.txt_custom_order.textChanged.connect(self._aggiorna_anteprima)
        self.btn_grp_sep.idClicked.connect(self._aggiorna_anteprima)
        self.txt_custom_sep.textChanged.connect(self._aggiorna_anteprima)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Conferma e Incolla")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._aggiorna_anteprima()

    def _inserisci_segnaposto_slots(self):
        if self.chk_custom_dir.isChecked():
            self.txt_custom_order.insertPlainText("{SLOTS}")

    def _on_custom_dir_toggled(self, checked: bool):
        self.txt_custom_order.setEnabled(checked)
        self._aggiorna_anteprima()

    def get_direzione_base(self) -> str:
        sel_id = self.btn_grp_dir.checkedId()
        return "verticale" if sel_id == 2 else "orizzontale"

    def get_direzione(self) -> str:
        if self.chk_custom_dir.isChecked():
            return "custom"
        return self.get_direzione_base()

    def get_separatore(self) -> str:
        sel_id = self.btn_grp_sep.checkedId()
        if sel_id == 1:
            return "\n"
        elif sel_id == 2:
            return ", "
        elif sel_id == 3:
            return "\t"
        elif sel_id == 4:
            return " "
        elif sel_id == 5:
            return self.txt_custom_sep.text()
        return "\n"

    def deve_disattivare_anteprima(self) -> bool:
        return self.chk_skip_preview.isChecked()

