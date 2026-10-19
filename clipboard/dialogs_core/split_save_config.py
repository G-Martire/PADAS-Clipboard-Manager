"""
PADAS CLIPBOARD MANAGER - DIALOGS CORE
Dialogo di configurazione per la funzionalità Split & Save (Copia Multipla) con diagramma grafico a frecce e linee tratteggiate.
"""

import math
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QLineEdit, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QGroupBox, QCheckBox,
    QFrame, QGridLayout
)
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QPolygon
from PyQt6.QtCore import Qt, QPoint


class GridPreviewWidget(QFrame):
    """Widget per l'anteprima visiva grafica che disegna frecce e connettori tratteggiati tra gli slot."""

    LAYOUT_DEFAULT_5X4 = [
        ["1", "2", "3", "4", "5"],
        ["Q", "W", "E", "R", "T"],
        ["A", "S", "D", "F", "G"],
        ["Z", "X", "C", "V", "B"]
    ]

    def __init__(self, layout_matrice: list = None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #f4fbf7;
                border: 1px solid #a8e6cf;
                border-radius: 6px;
            }
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                font-weight: bold;
                color: #2e7d32;
            }
        """)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(6)

        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        self.grid_layout.setSpacing(16)
        self.main_layout.addLayout(self.grid_layout)

        self.layout_matrice = layout_matrice if layout_matrice else self.LAYOUT_DEFAULT_5X4
        self.labels = {}
        self.seq_coords = []
        self._costruisci_griglia()

    def impilazione_layout(self, layout_matrice: list):
        """Aggiorna la matrice del layout visivo se cambia la tastiera."""
        if layout_matrice:
            self.layout_matrice = layout_matrice
            self._costruisci_griglia()

    def _costruisci_griglia(self):
        """Pulisce e ricostruisce la griglia di etichette leggendo i tasti reali del layout."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.labels.clear()

        max_r = min(len(self.layout_matrice), 4)
        for r_idx in range(max_r):
            riga = self.layout_matrice[r_idx]
            max_c = min(len(riga), 5)
            for c_idx in range(max_c):
                val = str(riga[c_idx]).strip().upper()
                lbl = QLabel(val if val else "-")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setFixedSize(32, 28)
                lbl.setStyleSheet("""
                    background-color: #ffffff;
                    border: 1px solid #c8e6c9;
                    border-radius: 4px;
                    color: #1b5e20;
                """)
                self.grid_layout.addWidget(lbl, r_idx, c_idx)
                self.labels[(r_idx, c_idx)] = lbl

    def aggiorna_frecce(self, direzione: str, n_val: int):
        """Calcola la sequenza degli slot attivi e forza il ridisegno delle frecce grafiche."""
        max_r = min(len(self.layout_matrice), 4)
        max_c = 5

        # Reset neutro
        for lbl in self.labels.values():
            lbl.setStyleSheet("""
                background-color: #ffffff;
                border: 1px solid #c8e6c9;
                border-radius: 4px;
                color: #1b5e20;
            """)

        # Calcolo sequenza coordinate (r, c)
        self.seq_coords.clear()
        if direzione == "orizzontale":
            for c in range(max_c):
                for r in range(min(n_val, max_r)):
                    if (r, c) in self.labels:
                        self.seq_coords.append((r, c))
        else:
            for r in range(max_r):
                for c in range(min(n_val, max_c)):
                    if (r, c) in self.labels:
                        self.seq_coords.append((r, c))

        # Evidenziazione degli slot attivi nella sequenza
        for r, c in self.seq_coords:
            lbl = self.labels[(r, c)]
            lbl.setStyleSheet("""
                background-color: #c8e6c9;
                border: 1px solid #2e7d32;
                border-radius: 4px;
                color: #1b5e20;
                font-weight: bold;
            """)

        self.update()  # Richiede l'esecuzione di paintEvent

    def paintEvent(self, event):
        """Disegna graficamente le frecce e le linee tratteggiate tra gli slot della sequenza."""
        super().paintEvent(event)

        if len(self.seq_coords) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for i in range(len(self.seq_coords) - 1):
            r1, c1 = self.seq_coords[i]
            r2, c2 = self.seq_coords[i + 1]

            if (r1, c1) not in self.labels or (r2, c2) not in self.labels:
                continue

            lbl1 = self.labels[(r1, c1)]
            lbl2 = self.labels[(r2, c2)]

            p1 = lbl1.geometry().center()
            p2 = lbl2.geometry().center()

            # Avanzamento diretto orizzontale o verticale
            is_passo_diretto = (r1 == r2 and c2 == c1 + 1) or (c1 == c2 and r2 == r1 + 1)

            if is_passo_diretto:
                pen = QPen(QColor("#2e7d32"), 2, Qt.PenStyle.SolidLine)
            else:
                pen = QPen(QColor("#2e7d32"), 2, Qt.PenStyle.DashLine)  # Tratteggio per il ritorno a capo

            painter.setPen(pen)

            # Calcolo dei punti sui bordi esterni delle caselle
            angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
            start_p = QPoint(
                int(p1.x() + 16 * math.cos(angle)),
                int(p1.y() + 16 * math.sin(angle))
            )
            end_p = QPoint(
                int(p2.x() - 16 * math.cos(angle)),
                int(p2.y() - 16 * math.sin(angle))
            )

            painter.drawLine(start_p, end_p)
            self._disegna_punta_freccia(painter, start_p, end_p)

    def _disegna_punta_freccia(self, painter: QPainter, p1: QPoint, p2: QPoint):
        """Disegna la punta della freccia a fine percorso."""
        angle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        arrow_size = 6

        p_arrow1 = QPoint(
            int(p2.x() - arrow_size * math.cos(angle - math.pi / 6)),
            int(p2.y() - arrow_size * math.sin(angle - math.pi / 6))
        )
        p_arrow2 = QPoint(
            int(p2.x() - arrow_size * math.cos(angle + math.pi / 6)),
            int(p2.y() - arrow_size * math.sin(angle + math.pi / 6))
        )

        painter.setBrush(QColor("#2e7d32"))
        polygon = QPolygon([p2, p_arrow1, p_arrow2])
        painter.drawPolygon(polygon)


class SplitSaveConfigDialog(QDialog):
    """Finestra di dialogo per la personalizzazione della logica Split & Save."""

    def __init__(self, config: dict = None, parent=None, layout_matrice: list = None):
        super().__init__(parent)
        self.setWindowTitle("Configurazione Split & Save (Copia Multipla)")
        self.resize(580, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.config = config or self._get_default_config()

        if not layout_matrice and parent and hasattr(parent, "keyboard_map") and parent.keyboard_map:
            layout_matrice = parent.keyboard_map._costruisci_layout_corrente()

        self.layout_matrice = layout_matrice or []
        self.init_ui()

    @staticmethod
    def _get_default_config() -> dict:
        return {
            "separatore_definito_in_testo": True,
            "separatore_default": "auto",
            "separatore_custom": "",
            "colonne_default": 4,
            "direzione_default": "orizzontale",
            "gestione_occupati": "trasla",
            "mostra_anteprima": True,
            "timeout_sec": 1.5
        }

    def init_ui(self):
        """Costruisce la struttura dell'interfaccia utente del dialogo."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 1. SEZIONE GERARCHIA E SEPARATORE
        grp_sep = QGroupBox("1. SEPARATORE E GERARCHIA")
        lay_sep = QVBoxLayout(grp_sep)

        self.chk_sep_in_testo = QCheckBox("Controlla se il separatore è specificato nell'intestazione del testo")
        self.chk_sep_in_testo.setChecked(self.config.get("separatore_definito_in_testo", True))
        lay_sep.addWidget(self.chk_sep_in_testo)

        lbl_sep_def = QLabel("Separatore Predefinito di Fallback:")
        lbl_sep_def.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lay_sep.addWidget(lbl_sep_def)

        lay_radios = QHBoxLayout()
        self.btn_grp_sep = QButtonGroup(self)

        radios_def = [
            ("Auto", "auto", 1),
            ("A capo (\\n)", "\n", 2),
            ("Punto e virgola (;)", ";", 3),
            ("Virgola (,)", ",", 4),
            ("Personalizzato", "custom", 5)
        ]

        sep_attuale = self.config.get("separatore_default", "auto")
        for label, val, idx in radios_def:
            rad = QRadioButton(label)
            self.btn_grp_sep.addButton(rad, idx)
            rad.setProperty("valore_sep", val)
            if sep_attuale == val:
                rad.setChecked(True)
            lay_radios.addWidget(rad)

        if not self.btn_grp_sep.checkedButton():
            self.btn_grp_sep.button(1).setChecked(True)

        lay_sep.addLayout(lay_radios)

        self.txt_custom_sep = QLineEdit()
        self.txt_custom_sep.setPlaceholderText("Inserisci separatore personalizzato (es: | o -)")
        self.txt_custom_sep.setText(self.config.get("separatore_custom", ""))
        lay_sep.addWidget(self.txt_custom_sep)

        layout.addWidget(grp_sep)

        # 2. SEZIONE LAYOUT E GRIGLIA TASTIERA CON ANTEPRIMA GRAFICA
        grp_layout = QGroupBox("2. LAYOUT E DIREZIONE SALVATAGGIO")
        lay_lay_main = QHBoxLayout(grp_layout)

        lay_lay_left = QVBoxLayout()

        self.lbl_n_param = QLabel("Altezza max colonne (N righe):")
        self.spn_colonne = QSpinBox()
        self.spn_colonne.setRange(1, 12)
        self.spn_colonne.setValue(self.config.get("colonne_default", 4))
        lay_lay_left.addWidget(self.lbl_n_param)
        lay_lay_left.addWidget(self.spn_colonne)

        self.btn_grp_dir = QButtonGroup(self)
        self.rad_oriz = QRadioButton("↔️ Orizzontale (per Colonne)")
        self.rad_vert = QRadioButton("↕️ Verticale (per Righe)")
        self.btn_grp_dir.addButton(self.rad_oriz, 1)
        self.btn_grp_dir.addButton(self.rad_vert, 2)

        if self.config.get("direzione_default", "orizzontale") == "verticale":
            self.rad_vert.setChecked(True)
            self.lbl_n_param.setText("Larghezza max righe (N colonne):")
        else:
            self.rad_oriz.setChecked(True)
            self.lbl_n_param.setText("Altezza max colonne (N righe):")

        lay_lay_left.addWidget(self.rad_oriz)
        lay_lay_left.addWidget(self.rad_vert)
        lay_lay_left.addStretch()

        lay_lay_main.addLayout(lay_lay_left, stretch=1)

        self.preview_widget = GridPreviewWidget(layout_matrice=self.layout_matrice, parent=self)
        lay_lay_main.addWidget(self.preview_widget, stretch=1)

        layout.addWidget(grp_layout)

        self.spn_colonne.valueChanged.connect(self._aggiorna_anteprima)
        self.rad_oriz.toggled.connect(self._on_direzione_changed)
        self.rad_vert.toggled.connect(self._on_direzione_changed)

        self._aggiorna_anteprima()

        # 3. SEZIONE CONFLITTI E TIMEOUT
        grp_conf = QGroupBox("3. GESTIONE CONFLITTI E TIMEOUT")
        lay_conf = QVBoxLayout(grp_conf)

        self.btn_grp_conf = QButtonGroup(self)
        self.rad_trasla = QRadioButton("📦 Trasla i vecchi dati occupati (sbloccati) negli slot successivi")
        self.rad_sovrascrivi = QRadioButton("⚠️ Sovrascrivi i dati negli slot occupati (sbloccati)")
        self.btn_grp_conf.addButton(self.rad_trasla, 1)
        self.btn_grp_conf.addButton(self.rad_sovrascrivi, 2)

        if self.config.get("gestione_occupati", "trasla") == "sovrascrivi":
            self.rad_sovrascrivi.setChecked(True)
        else:
            self.rad_trasla.setChecked(True)

        lay_conf.addWidget(self.rad_trasla)
        lay_conf.addWidget(self.rad_sovrascrivi)

        lay_time = QHBoxLayout()
        lbl_time = QLabel("Timeout attesa tasti sequenza (secondi):")
        self.spn_timeout = QDoubleSpinBox()
        self.spn_timeout.setRange(0.5, 5.0)
        self.spn_timeout.setSingleStep(0.1)
        self.spn_timeout.setValue(self.config.get("timeout_sec", 1.5))
        lay_time.addWidget(lbl_time)
        lay_time.addWidget(self.spn_timeout)
        lay_conf.addLayout(lay_time)

        self.chk_anteprima = QCheckBox("Mostra il pop-up di anteprima se il separatore è ambiguo")
        self.chk_anteprima.setChecked(self.config.get("mostra_anteprima", True))
        lay_conf.addWidget(self.chk_anteprima)

        layout.addWidget(grp_conf)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_direzione_changed(self):
        """Aggiorna le etichette quando si passa da Orizzontale a Verticale e viceversa."""
        if self.rad_oriz.isChecked():
            self.lbl_n_param.setText("Altezza max colonne (N righe):")
        else:
            self.lbl_n_param.setText("Larghezza max righe (N colonne):")
        self._aggiorna_anteprima()

    def _aggiorna_anteprima(self):
        """Notifica il widget di anteprima per ridisegnare la selezione e le frecce."""
        direzione = "orizzontale" if self.rad_oriz.isChecked() else "verticale"
        n_val = self.spn_colonne.value()
        self.preview_widget.aggiorna_frecce(direzione, n_val)

    def get_config(self) -> dict:
        """Restituisce il dizionario di configurazione aggiornato."""
        btn_sep = self.btn_grp_sep.checkedButton()
        val_sep = btn_sep.property("valore_sep") if btn_sep else "auto"

        return {
            "separatore_definito_in_testo": self.chk_sep_in_testo.isChecked(),
            "separatore_default": val_sep,
            "separatore_custom": self.txt_custom_sep.text(),
            "colonne_default": self.spn_colonne.value(),
            "direzione_default": "verticale" if self.rad_vert.isChecked() else "orizzontale",
            "gestione_occupati": "sovrascrivi" if self.rad_sovrascrivi.isChecked() else "trasla",
            "mostra_anteprima": self.chk_anteprima.isChecked(),
            "timeout_sec": self.spn_timeout.value()
        }

