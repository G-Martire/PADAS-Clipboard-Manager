"""
PADAS CLIPBOARD MANAGER - MAKE FILES OPTIONS DIALOG
Finestra di dialogo per la configurazione della creazione automatica di file e cartelle (Shift + Alt + M).
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
    QLineEdit, QCheckBox, QDialogButtonBox, QGroupBox, QListWidget, QAbstractItemView
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class MakeFilesOptionsDialog(QDialog):
    """Dialogo per configurare come interpretare gli elementi e le estensioni per la creazione di file e cartelle."""

    def __init__(self, elementi: list[str], cartella_base=None, config: dict = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurazione Creazione File e Cartelle")
        self.resize(500, 480)

        # Imposta la finestra sempre in primo piano (Sopra tutti i programmi)
        flags = self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        flags &= ~Qt.WindowType.WindowContextHelpButtonHint
        self.setWindowFlags(flags)

        self.elementi = elementi or []
        self.cartella_base = cartella_base
        self.config = config or {}
        
        self.init_ui()

    def showEvent(self, event):
        """Forza il pop-up a salire in primo piano ed a prendere subito il focus all'apertura."""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def init_ui(self):
        """Inizializza l'interfaccia utente del dialogo."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 1. Opzioni di interpretazione della cartella
        grp_opt = QGroupBox("Modalità Interpretazione Cartella Destinazione")
        lay_opt = QVBoxLayout(grp_opt)

        self.btn_grp = QButtonGroup(self)
        self.rad_primo = QRadioButton("📁 Il PRIMO elemento è il nome della cartella (gli altri sono file)")
        self.rad_ultimo = QRadioButton("📁 L'ULTIMO elemento è il nome della cartella (gli altri sono file)")
        self.rad_nessuno = QRadioButton("📄 Tutti gli elementi sono file (crea nella cartella corrente)")

        self.btn_grp.addButton(self.rad_primo, 1)
        self.btn_grp.addButton(self.rad_ultimo, 2)
        self.btn_grp.addButton(self.rad_nessuno, 3)

        # Ripristina modalità salvata o usa default
        id_salvato = self.config.get("modalita_cartella", 1 if len(self.elementi) > 1 else 3)
        if id_salvato == 1 and len(self.elementi) > 1:
            self.rad_primo.setChecked(True)
        elif id_salvato == 2 and len(self.elementi) > 1:
            self.rad_ultimo.setChecked(True)
        else:
            self.rad_nessuno.setChecked(True)

        lay_opt.addWidget(self.rad_primo)
        lay_opt.addWidget(self.rad_ultimo)
        lay_opt.addWidget(self.rad_nessuno)
        layout.addWidget(grp_opt)

        # 2. Cartella Personalizzata (opzionale)
        grp_custom = QGroupBox("Cartella di Destinazione Personalizzata (opzionale)")
        lay_custom = QVBoxLayout(grp_custom)
        self.txt_custom_folder = QLineEdit()
        self.txt_custom_folder.setPlaceholderText("Lascia vuoto per usare la regola selezionata sopra...")
        lay_custom.addWidget(self.txt_custom_folder)
        layout.addWidget(grp_custom)

        # 3. Estensione Predefinita Automatica
        grp_ext = QGroupBox("Gestione Estensione File")
        lay_ext = QHBoxLayout(grp_ext)

        self.chk_auto_ext = QCheckBox("Aggiungi estensione se mancante:")
        self.chk_auto_ext.setChecked(self.config.get("auto_ext_attivo", True))

        self.txt_ext_value = QLineEdit()
        self.txt_ext_value.setText(self.config.get("ext_default", ".py"))
        self.txt_ext_value.setMaximumWidth(100)
        self.txt_ext_value.setEnabled(self.chk_auto_ext.isChecked())

        lay_ext.addWidget(self.chk_auto_ext)
        lay_ext.addWidget(self.txt_ext_value)
        lay_ext.addStretch()
        layout.addWidget(grp_ext)

        # 4. Anteprima Risultato
        grp_prev = QGroupBox("Anteprima File da Creare")
        lay_prev = QVBoxLayout(grp_prev)

        self.lbl_dest = QLabel("Cartella: .")
        self.lbl_dest.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lay_prev.addWidget(self.lbl_dest)

        self.lst_preview = QListWidget()
        self.lst_preview.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        lay_prev.addWidget(self.lst_preview)
        layout.addWidget(grp_prev)

        # Connessioni per l'aggiornamento dinamico dell'anteprima
        self.btn_grp.buttonToggled.connect(self._aggiorna_anteprima)
        self.txt_custom_folder.textChanged.connect(self._aggiorna_anteprima)
        self.chk_auto_ext.toggled.connect(self._on_chk_ext_toggled)
        self.txt_ext_value.textChanged.connect(self._aggiorna_anteprima)

        self._aggiorna_anteprima()

        # Bottoni OK / Annulla
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_chk_ext_toggled(self, checked: bool):
        """Abilita o disabilita il campo di testo dell'estensione ed aggiorna l'anteprima."""
        self.txt_ext_value.setEnabled(checked)
        self._aggiorna_anteprima()

    def _applica_estensione_file(self, nome_file: str) -> str:
        """Aggiunge l'estensione predefinita al nome file se questo ne è sprovvisto."""
        if not self.chk_auto_ext.isChecked():
            return nome_file

        ext_scelta = self.txt_ext_value.text().strip()
        if not ext_scelta:
            return nome_file

        if not ext_scelta.startswith("."):
            ext_scelta = "." + ext_scelta

        path_obj = Path(nome_file)
        # Se il file non ha alcuna estensione (es: 'text_splitter' o '__init__')
        if not path_obj.suffix:
            return nome_file + ext_scelta

        return nome_file

    def _aggiorna_anteprima(self):
        """Aggiorna l'etichetta della cartella e la lista dei file nell'anteprima."""
        cartella, file_list = self.get_cartella_e_file()

        if self.cartella_base:
            p_full = Path(self.cartella_base) / cartella if cartella else Path(self.cartella_base)
            dest_str = f"Cartella: {p_full}"
        else:
            dest_str = f"Cartella: {cartella}" if cartella else "Cartella: . (Radice Progetto)"

        self.lbl_dest.setText(dest_str)

        self.lst_preview.clear()
        for f in file_list:
            self.lst_preview.addItem(f"📄 {f}")

    def get_cartella_e_file(self) -> tuple[str, list[str]]:
        """Restituisce la tupla (cartella_destinazione, lista_nomi_file_elaborati)."""
        custom_folder = self.txt_custom_folder.text().strip()
        sel_id = self.btn_grp.checkedId()

        if custom_folder:
            cartella_raw = custom_folder
            file_raw = list(self.elementi)
        elif sel_id == 1 and len(self.elementi) > 1:
            cartella_raw = self.elementi[0]
            file_raw = self.elementi[1:]
        elif sel_id == 2 and len(self.elementi) > 1:
            cartella_raw = self.elementi[-1]
            file_raw = self.elementi[:-1]
        else:
            cartella_raw = ""
            file_raw = list(self.elementi)

        file_processati = [self._applica_estensione_file(f) for f in file_raw]
        return cartella_raw, file_processati

    def get_configurazione(self) -> dict:
        """Restituisce le impostazioni correnti da salvare per i futuri utilizzi."""
        return {
            "modalita_cartella": self.btn_grp.checkedId(),
            "auto_ext_attivo": self.chk_auto_ext.isChecked(),
            "ext_default": self.txt_ext_value.text().strip()
        }

