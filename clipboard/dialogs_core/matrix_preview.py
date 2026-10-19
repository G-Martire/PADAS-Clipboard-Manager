"""
PADAS CLIPBOARD MANAGER - DIALOGS CORE
Widget grafico che disegna i tasti reali della matrice e le frecce vettoriali di collegamento.
"""

from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QPolygonF
from PyQt6.QtCore import Qt, QPointF


class MatrixPreviewWidget(QFrame):
    """Widget grafico che disegna i tasti reali della matrice e le frecce vettoriali di collegamento."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            MatrixPreviewWidget {
                background-color: #f9fbe7;
                border: 1px dashed #a5d6a7;
                border-radius: 6px;
            }
        """)
        self.setFixedSize(200, 150)
        self.modalita = "orizzontale"

        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(12, 12, 12, 12)
        self.grid.setSpacing(2)

        self.tasti_labels = {}
        self.frecce_oriz = {}
        self.frecce_vert = {}

        self._costruisci_griglia_grafica()

    def _costruisci_griglia_grafica(self):
        matrice_tasti = [
            ['1', '2', '3'],
            ['Q', 'W', 'E'],
            ['A', 'S', 'D']
        ]

        style_tasto = """
            QLabel {
                background-color: #e8f5e9;
                border: 1px solid #81c784;
                border-radius: 4px;
                color: #1b4332;
                font-weight: bold;
                font-size: 10pt;
            }
        """

        style_freccia = "color: #2e7d32; font-weight: bold; font-size: 9pt;"

        for r in range(3):
            for c in range(3):
                tasto_char = matrice_tasti[r][c]
                lbl_tasto = QLabel(tasto_char)
                lbl_tasto.setFixedSize(28, 28)
                lbl_tasto.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_tasto.setStyleSheet(style_tasto)
                
                grid_r = r * 2
                grid_c = c * 2
                self.grid.addWidget(lbl_tasto, grid_r, grid_c)
                self.tasti_labels[tasto_char] = lbl_tasto

                if c < 2:
                    lbl_f_oriz = QLabel("")
                    lbl_f_oriz.setFixedSize(16, 28)
                    lbl_f_oriz.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl_f_oriz.setStyleSheet(style_freccia)
                    self.grid.addWidget(lbl_f_oriz, grid_r, grid_c + 1)
                    self.frecce_oriz[(r, c)] = lbl_f_oriz

                if r < 2:
                    lbl_f_vert = QLabel("")
                    lbl_f_vert.setFixedSize(28, 14)
                    lbl_f_vert.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl_f_vert.setStyleSheet(style_freccia)
                    self.grid.addWidget(lbl_f_vert, grid_r + 1, grid_c)
                    self.frecce_vert[(r, c)] = lbl_f_vert

    def aggiorna_modalita(self, modalita: str):
        # Se la modalità è custom, non sovrascrive il disegno della modalità base selezionata
        if modalita in ["orizzontale", "verticale"]:
            self.modalita = modalita

        for lbl in self.frecce_oriz.values():
            lbl.setText("")
        for lbl in self.frecce_vert.values():
            lbl.setText("")

        if self.modalita == "orizzontale":
            for r in range(3):
                self.frecce_oriz[(r, 0)].setText("➔")
                self.frecce_oriz[(r, 1)].setText("➔")

        elif self.modalita == "verticale":
            for c in range(3):
                self.frecce_vert[(0, c)].setText("🠋")
                self.frecce_vert[(1, c)].setText("🠋")

        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor("#2e7d32"), 1.8, Qt.PenStyle.DashLine)
        painter.setPen(pen)

        if self.modalita == "orizzontale":
            # Collegamenti a capo con punta orientata correttamente verso Q e A
            self._disegna_freccia_diagonale(painter, self.tasti_labels['3'], self.tasti_labels['Q'])
            self._disegna_freccia_diagonale(painter, self.tasti_labels['E'], self.tasti_labels['A'])

        elif self.modalita == "verticale":
            # Collegamenti a risalita con punta orientata verso 2 e 3
            self._disegna_freccia_diagonale(painter, self.tasti_labels['A'], self.tasti_labels['2'])
            self._disegna_freccia_diagonale(painter, self.tasti_labels['S'], self.tasti_labels['3'])

    def _disegna_freccia_diagonale(self, painter: QPainter, widget_da: QWidget, widget_a: QWidget):
        pt_start = widget_da.geometry().center()
        pt_end = widget_a.geometry().center()

        painter.drawLine(pt_start, pt_end)

        line_vec = QPointF(pt_end - pt_start)
        length = (line_vec.x()**2 + line_vec.y()**2)**0.5
        if length == 0:
            return

        norm_vec = line_vec / length
        perp_vec = QPointF(-norm_vec.y(), norm_vec.x())

        arrow_size = 7.0
        p1 = QPointF(pt_end) - norm_vec * arrow_size + perp_vec * (arrow_size / 2.0)
        p2 = QPointF(pt_end) - norm_vec * arrow_size - perp_vec * (arrow_size / 2.0)

        old_brush = painter.brush()
        painter.setBrush(QColor("#2e7d32"))
        painter.drawPolygon(QPolygonF([QPointF(pt_end), p1, p2]))
        painter.setBrush(old_brush)

