"""
PADAS CLIPBOARD MANAGER - MENU E TOOLBAR EVENTS
Gestisce i collegamenti e gli eventi della barra dei menu, della toolbar e dei pulsanti di finestra.
"""

from PyQt6.QtWidgets import QMessageBox
from ..dialogs_core import OpzioniNotificheDialog, SplitSaveConfigDialog
from ..io import ClipboardIO


class MenuToolbarEventsMixin:
    """Mixin per la gestione degli eventi di menu, toolbar e finestra."""

    def _connetti_azioni(self):
        """Collega i segnali della GUI, dei pulsanti della barra titolo, della toolbar e dei menu."""
        self.btn_nascondi.clicked.connect(self.hide)
        self.btn_riduci.clicked.connect(self.showMinimized)
        self.btn_ingrandisci.clicked.connect(self._toggle_maximize)
        self.btn_chiudi.clicked.connect(self.close)

        # Menu File - Importazioni
        self.act_import_json.triggered.connect(lambda: ClipboardIO.import_json(self, self.memoria, self._refresh))
        self.act_import_excel.triggered.connect(lambda: ClipboardIO.import_excel(self, self.memoria, self.elementi_massivi, self._refresh))
        self.act_import_csv.triggered.connect(lambda: ClipboardIO.import_csv(self, self.memoria, self.elementi_massivi, self._refresh))
        
        # Menu File - Esportazioni
        self.act_export_rapido.triggered.connect(self._esegui_export_rapido)
        self.act_export_custom.triggered.connect(lambda: ClipboardIO.export_as_json(self, self.memoria, self.elementi_massivi))
        
        self.act_svuota.triggered.connect(self.clear_memory)

        # Menu Strumenti & Guida
        self.act_opzioni_notifica.triggered.connect(self.apri_opzioni_notifiche)
        self.act_config_split_save.triggered.connect(self.apri_config_split_save)
        self.act_scorciatoie.triggered.connect(self.mostra_legenda_scorciatoie)

        # Toolbar
        self.btn_massiva.clicked.connect(self.toggle_cattura_massiva)
        self.btn_toggle_path.clicked.connect(self.toggle_vista_percorso)
        self.btn_lock_selected.clicked.connect(self.toggle_blocco_selezionati)
        self.btn_toggle_keyboard.clicked.connect(self.toggle_mappa_tastiera)
        self.btn_help.clicked.connect(self.mostra_legenda_scorciatoie)
        self.btn_split_save_config.clicked.connect(self.apri_config_split_save)

        # Interazione Click Tasto Virtuale Mappa -> Seleziona Riga in Tabella
        if hasattr(self, 'keyboard_map'):
            self.keyboard_map.slot_selected.connect(self._seleziona_riga_da_slot)

        self.table.cellChanged.connect(self._on_cell_changed)

    def toggle_cattura_massiva(self):
        """Attiva o disattiva la modalità di cattura massiva."""
        self.cattura_massiva_attiva = self.btn_massiva.isChecked()
        if self.cattura_massiva_attiva:
            self.btn_massiva.setText("Cattura Massiva: ON")
            self.btn_massiva.setStyleSheet("background-color: #2e7d32; color: white;")
        else:
            self.btn_massiva.setText("Cattura Massiva: OFF")
            self.btn_massiva.setStyleSheet("")

    def apri_opzioni_notifiche(self):
        """Apre il dialogo delle opzioni di notifica."""
        dlg = OpzioniNotificheDialog(self.config_notifiche, self)
        if dlg.exec():
            self.config_notifiche = dlg.get_config()

    def apri_config_split_save(self):
        """Apre il dialogo per la configurazione di Split & Save."""
        config_attuale = getattr(self, "config_split_save", {})
        dlg = SplitSaveConfigDialog(config_attuale, self)
        if dlg.exec():
            self.config_split_save = dlg.get_config()

    def mostra_legenda_scorciatoie(self):
        """Mostra la finestra di dialogo con la legenda delle scorciatoie."""
        legenda = (
            "<b>Legenda Scorciatoie Rapide PADAS Clipboard:</b><br><br>"
            "• <b>Shift + Alt + Z</b> poi [Tasto Slot] → Salva dalla clipboard allo slot scelto<br>"
            "• <b>Shift + Alt + A</b> poi [Slot Inizio] → Split & Save (Copia Multipla)<br>"
            "• <b>Shift + Alt + D</b> poi [Tasto Slot] → Incolla contenuto dallo slot scelto<br>"
            "• <b>Shift + Alt + Q</b> poi [Tasto Slot] → Blocca / Sblocca Slot (🔒 Protetto)<br>"
            "• <b>Shift + Alt + W</b> poi [Tasto Slot] → Cancella slot (Se bloccato viene ignorato)<br>"
            "• <b>Shift + Alt + W + Q + E</b> → Svuota TUTTO (Tranne slot bloccati 🔒)<br>"
            "• <b>Shift + Alt + X</b> poi [Tasto Slot] → Prendi da Clipboard di sistema<br>"
            "• <b>Shift + Alt + F</b> poi [Tasto Slot] → Copia Formato Selettivo<br>"
            "• <b>Shift + Alt + G</b> poi [Preset] poi [Destinazione] → Applica Preset<br>"
            "• <b>Shift + Alt + S</b> → Mostra/Nascondi questa finestra"
        )
        QMessageBox.information(self, "Legenda Scorciatoie Rapide", legenda)

    def toggle_vista_percorso(self):
        """Alterna la visualizzazione tra Solo Nome File e Percorso Completo."""
        self.mostra_percorso_completo = self.btn_toggle_path.isChecked()
        if self.mostra_percorso_completo:
            self.btn_toggle_path.setText("Vista File: Percorso Completo")
            self.btn_toggle_path.setStyleSheet("background-color: #1565c0; color: white;")
        else:
            self.btn_toggle_path.setText("Vista File: Solo Nome")
            self.btn_toggle_path.setStyleSheet("")
        
        self._refresh()

    def toggle_mappa_tastiera(self):
        """Mostra o nasconde la Mappa Tastiera."""
        visibile = self.btn_toggle_keyboard.isChecked()
        self.keyboard_map.setVisible(visibile)
        if visibile:
            self.btn_toggle_keyboard.setStyleSheet("background-color: #2e7d32; color: white;")
        else:
            self.btn_toggle_keyboard.setStyleSheet("")

    def _esegui_export_rapido(self):
        """Salva direttamente nel percorso di default locale."""
        path_target = getattr(self, "percorso_autosalvataggio", None)
        ClipboardIO.save_to_json(self, self.memoria, self.elementi_massivi, target_path=path_target)
        destinazione_str = str(path_target.resolve()) if path_target else "cartella predefinita"
        QMessageBox.information(self, "Esportazione Rapida", f"Dati salvati rapidamente in:\n{destinazione_str}")