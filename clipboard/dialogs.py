"""
PADAS CLIPBOARD MANAGER - DIALOGS E FINESTRE DI CONFIGURAZIONE
Contiene il dialog per il filtraggio selettivo dei formati e le opzioni notifiche.
"""

import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QLineEdit, QTextEdit, QPushButton, QDialogButtonBox, QGroupBox, QCheckBox,
    QGridLayout, QFrame, QWidget
)
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QPolygonF
from PyQt6.QtCore import Qt, QPointF



class FormatoFilterDialog(QDialog):
    """Dialog che permette all'utente di selezionare quali proprietà di stile estrarre (Shift + Alt + F)."""

    def __init__(self, config_smart: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filtro Formato Avanzato (Shift + Alt + F)")
        self.resize(400, 360)

        layout = QVBoxLayout(self)

        # Toggle Auto-Smart Mode
        self.chk_auto_smart = QCheckBox("Attiva Riconoscimento Automatico (Auto-Smart Mode)")
        self.chk_auto_smart.setToolTip("Rileva automaticamente se il contenuto è Testo o Tabella ed applica il rispettivo preset su Shift+Alt+G")
        auto_smart_attivo = config_smart.get("auto_smart", True) if config_smart else True
        self.chk_auto_smart.setChecked(auto_smart_attivo)
        layout.addWidget(self.chk_auto_smart)

        # Gruppo Testo
        grp_testo = QGroupBox("Proprietà Testo")
        lyt_testo = QVBoxLayout()
        self.chk_font = QCheckBox("Tipo di Carattere (Font Family)")
        self.chk_size = QCheckBox("Dimensione Testo")
        self.chk_bold_italic = QCheckBox("Grassetto / Corsivo / Sottolineato")
        self.chk_color = QCheckBox("Colore Testo")

        self.chk_font.setChecked(True)
        self.chk_size.setChecked(True)
        self.chk_bold_italic.setChecked(True)
        self.chk_color.setChecked(True)

        lyt_testo.addWidget(self.chk_font)
        lyt_testo.addWidget(self.chk_size)
        lyt_testo.addWidget(self.chk_bold_italic)
        lyt_testo.addWidget(self.chk_color)
        grp_testo.setLayout(lyt_testo)
        layout.addWidget(grp_testo)

        # Gruppo Tabella e Sfondo
        grp_tabella = QGroupBox("Celle e Tabelle")
        lyt_tabella = QVBoxLayout()
        self.chk_bg_color = QCheckBox("Colore Sfondo / Evidenziazione")
        self.chk_borders = QCheckBox("Bordi e Spessore Tabelle")
        self.chk_align = QCheckBox("Allineamento (Sinistra, Centro, Destra)")

        self.chk_bg_color.setChecked(True)
        self.chk_borders.setChecked(True)
        self.chk_align.setChecked(True)

        lyt_tabella.addWidget(self.chk_bg_color)
        lyt_tabella.addWidget(self.chk_borders)
        lyt_tabella.addWidget(self.chk_align)
        grp_tabella.setLayout(lyt_tabella)
        layout.addWidget(grp_tabella)

        # Pulsanti Preset veloci
        preset_layout = QHBoxLayout()
        btn_preset_text = QPushButton("Preset Solo Testo")
        btn_preset_text.clicked.connect(self._preset_solo_testo)
        btn_preset_table = QPushButton("Preset Solo Tabella")
        btn_preset_table.clicked.connect(self._preset_solo_tabella)
        preset_layout.addWidget(btn_preset_text)
        preset_layout.addWidget(btn_preset_table)
        layout.addLayout(preset_layout)

        # Pulsanti OK / Annulla
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("Conferma e Salva in Slot")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Annulla")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def _preset_solo_testo(self):
        self.chk_font.setChecked(True)
        self.chk_size.setChecked(True)
        self.chk_bold_italic.setChecked(True)
        self.chk_color.setChecked(True)
        self.chk_bg_color.setChecked(False)
        self.chk_borders.setChecked(False)
        self.chk_align.setChecked(False)

    def _preset_solo_tabella(self):
        self.chk_font.setChecked(False)
        self.chk_size.setChecked(False)
        self.chk_bold_italic.setChecked(False)
        self.chk_color.setChecked(False)
        self.chk_bg_color.setChecked(True)
        self.chk_borders.setChecked(True)
        self.chk_align.setChecked(True)

    def get_filtri(self) -> dict:
        return {
            "auto_smart": self.chk_auto_smart.isChecked(),
            "font": self.chk_font.isChecked(),
            "size": self.chk_size.isChecked(),
            "bold_italic": self.chk_bold_italic.isChecked(),
            "color": self.chk_color.isChecked(),
            "bg_color": self.chk_bg_color.isChecked(),
            "borders": self.chk_borders.isChecked(),
            "align": self.chk_align.isChecked()
        }


class OpzioniNotificheDialog(QDialog):
    """Dialog per personalizzare la notifica durante la cattura/incollo."""

    def __init__(self, config_attuale: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opzioni Notifiche PADAS Clipboard")
        self.resize(320, 220)

        layout = QVBoxLayout(self)

        grp = QGroupBox("Tipo di Notifica al Salvataggio")
        lyt_grp = QVBoxLayout()

        self.rad_bip = QRadioButton("Bip Acustico di Sistema")
        self.rad_icona = QRadioButton("Solo Icona / Nessun Pop-up")
        self.rad_popup = QRadioButton("Pop-up Notifica Veloce")

        tipo_attuale = config_attuale.get("tipo", "bip")
        if tipo_attuale == "bip":
            self.rad_bip.setChecked(True)
        elif tipo_attuale == "popup":
            self.rad_popup.setChecked(True)
        else:
            self.rad_icona.setChecked(True)

        lyt_grp.addWidget(self.rad_bip)
        lyt_grp.addWidget(self.rad_icona)
        lyt_grp.addWidget(self.rad_popup)
        grp.setLayout(lyt_grp)
        layout.addWidget(grp)

        btn_ok = QPushButton("Salva Opzioni")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

    def get_config(self) -> dict:
        if self.rad_bip.isChecked():
            return {"tipo": "bip"}
        elif self.rad_popup.isChecked():
            return {"tipo": "popup"}
        else:
            return {"tipo": "icona"}


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


class MultiPasteOptionsDialog(QDialog):
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

        # Selezione Quadrata (CheckBox) per l'ordine personalizzato
        self.chk_custom_dir = QCheckBox("🔀 Personalizzate e poi vert. / oriz.")
        layout_dir_options.addWidget(self.chk_custom_dir)

        # Header/Pulsante Rapido per Inserimento Segnaposto
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

        # Editor Multilinea (5 Righe fisso)
        self.txt_custom_order = QTextEdit()
        self.txt_custom_order.setFixedHeight(85)
        self.txt_custom_order.setPlaceholderText('Es:\n"Gentile cliente,"\n{SLOTS}\n"Cordiali saluti"')
        self.txt_custom_order.setEnabled(False)
        layout_dir_options.addWidget(self.txt_custom_order)

        layout_dir_main.addLayout(layout_dir_options)

        # WIDGET GRAFICO REALE della matrice
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

        # 4. ANTEPRIMA TESTO
        lbl_preview = QLabel("ANTEPRIMA:")
        lbl_preview.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        layout.addWidget(lbl_preview)

        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        self.txt_preview.setStyleSheet("background-color: #f1f8e9; color: #1b4332; font-size: 9pt;")
        layout.addWidget(self.txt_preview)

        # 5. FOOTER
        self.chk_skip_preview = QCheckBox("Non mostrare più l'anteprima (Incolla subito in futuro)")
        self.chk_skip_preview.setFont(QFont("Segoe UI", 8))
        layout.addWidget(self.chk_skip_preview)

        # Collegamenti eventi
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
        """Inserisce la tag {SLOTS} nel punto in cui si trova il cursore dell'editor."""
        if self.chk_custom_dir.isChecked():
            self.txt_custom_order.insertPlainText("{SLOTS}")

    def _on_custom_dir_toggled(self, checked: bool):
        self.txt_custom_order.setEnabled(checked)
        self._aggiorna_anteprima()

    def get_direzione_base(self) -> str:
        sel_id = self.btn_grp_dir.checkedId()
        return "verticale" if sel_id == 2 else "orizzontale"

    def get_direzione(self) -> str:
        """Restituisce la direzione corrente ('custom', 'verticale' o 'orizzontale')."""
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

    def get_testo_assemblato(self) -> str:
        direzione_base = self.get_direzione_base()
        sep = self.get_separatore()

        # Ordinamento principale degli slot compresi nelle coordinate
        elementi = list(self.slot_trovati)
        if direzione_base == "verticale":
            elementi.sort(key=lambda x: (x.get("colonna", 0), x.get("riga", 0)))
        else:
            elementi.sort(key=lambda x: (x.get("riga", 0), x.get("colonna", 0)))

        blocco_slots_unito = sep.join([item.get("dato", "") for item in elementi if item.get("dato")])

        # Se la personalizzazione multilinea è attiva
        if self.chk_custom_dir.isChecked() and self.txt_custom_order.toPlainText().strip():
            raw_text = self.txt_custom_order.toPlainText()
            
            # 1. Gestione segnaposto {SLOTS}
            if "{SLOTS}" in raw_text:
                risultato = raw_text.replace("{SLOTS}", blocco_slots_unito)
            else:
                # 2. Parsing per token, slot singoli e stringhe tra virgolette
                tokens = re.findall(r'"([^"]*)"|([^\s,\n]+)', raw_text)
                parti = []
                for t_literal, t_slot in tokens:
                    if t_literal:
                        parti.append(t_literal)
                    elif t_slot:
                        s_clean = t_slot.strip().lower()
                        # Se il token è esplicitamente \n inseriamo un andata a capo
                        if s_clean == "\\n":
                            parti.append("\n")
                        else:
                            item = next((e for e in self.slot_trovati if e.get("slot", "").strip().lower() == s_clean), None)
                            if item and item.get("dato"):
                                parti.append(item.get("dato"))
                risultato = sep.join(parti) if parti else raw_text

            # Convertiamo eventuali sequenze \n scritte nel testo generico in vere andate a capo
            return risultato.replace("\\n", "\n")

        return blocco_slots_unito

    def _aggiorna_anteprima(self):
        direzione_base = self.get_direzione_base()
        self.preview_matrix_widget.aggiorna_modalita(direzione_base)
        self.txt_preview.setPlainText(self.get_testo_assemblato())

    def get_struttura_personalizzata(self) -> str:
        """Restituisce il testo multilinea della struttura personalizzata."""
        return self.txt_custom_order.toPlainText()

    def is_custom_dir_attivo(self) -> bool:
        """Restituisce True se la casella di personalizzazione è spuntata."""
        return self.chk_custom_dir.isChecked()

