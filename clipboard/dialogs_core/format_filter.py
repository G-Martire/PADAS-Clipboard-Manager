"""
PADAS CLIPBOARD MANAGER - DIALOGS CORE
Filtro Formato Avanzato per la selezione delle proprietà di stile (Shift + Alt + F).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QCheckBox
)


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

