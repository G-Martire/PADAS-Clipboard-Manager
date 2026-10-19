"""
PADAS CLIPBOARD MANAGER - DIALOGS CORE
Dialog per la personalizzazione delle notifiche di cattura e salvataggio.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGroupBox, QRadioButton, QPushButton
)


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

