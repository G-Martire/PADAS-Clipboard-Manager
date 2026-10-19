"""
PADAS CLIPBOARD MANAGER - KEYBOARD CONFIG DIALOG
Gestisce la finestra di dialogo per la scelta dei preset di tastiera e l'inserimento dei tasti extra.
"""

from PyQt6.QtWidgets import (
    QDialog, QComboBox, QLineEdit, QFormLayout, QDialogButtonBox
)


class KeyboardConfigDialog(QDialog):
    """Dialogo per la selezione del preset di tastiera e la personalizzazione dei tasti aggiuntivi[cite: 3]."""

    PRESETS = {
        "Italiana Standard (ISO)": [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "'", "ì"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "è", "+"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ò", "à", "ù"],
            ["z", "x", "c", "v", "b", "n", "m", ",", ".", "-"]
        ],
        "Compatta Alfa (QWERTY Base)": [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m"]
        ],
        "ANSI US (Inglese)": [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'"],
            ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"]
        ]
    }

    def __init__(self, current_config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Personalizza Mappa Tastiera")
        self.resize(380, 200)

        layout = QFormLayout(self)

        # Selezione Preset Layout
        self.combo_preset = QComboBox(self)
        self.combo_preset.addItems(self.PRESETS.keys())
        preset_corrente = current_config.get("preset_name", "Italiana Standard (ISO)")
        idx = self.combo_preset.findText(preset_corrente)
        if idx >= 0:
            self.combo_preset.setCurrentIndex(idx)

        layout.addRow("Preset Layout:", self.combo_preset)

        # Campo Tasti Personalizzati Aggiuntivi
        self.txt_custom_keys = QLineEdit(self)
        self.txt_custom_keys.setPlaceholderText("Es: @, #, $, %, ç (separati da virgola)")
        tasti_custom = current_config.get("custom_keys", "")
        self.txt_custom_keys.setText(tasti_custom)

        layout.addRow("Tasti Extra / Personalizzati:", self.txt_custom_keys)

        # Pulsanti OK / Annulla
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_config(self) -> dict:
        preset_nome = self.combo_preset.currentText()
        custom_raw = self.txt_custom_keys.text().strip()
        return {
            "preset_name": preset_nome,
            "custom_keys": custom_raw
        }

