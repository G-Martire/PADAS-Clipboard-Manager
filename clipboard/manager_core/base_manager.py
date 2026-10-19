"""
PADAS CLIPBOARD MANAGER - BASE MANAGER
Gestisce l'inizializzazione dello stato, il caricamento automatico e il ciclo di vita (closeEvent).
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from ..gui_core import ClipboardGUI
from ..hotkeys import HotkeyManager
from ..io import ClipboardIO


class PadasClipboardManagerBase(ClipboardGUI):
    """Classe base per l'inizializzazione dello stato e la gestione della chiusura."""

    def __init__(self):
        super().__init__()
        self.memoria = []  # Struttura dati a Lista con ID univoci
        self.elementi_massivi = []
        self.cattura_massiva_attiva = False
        self.mostra_percorso_completo = False  # False = Solo Nome File | True = Percorso Completo
        self.config_notifiche = {"tipo": "bip"}
        self._blocco_cattura_massiva = False  # Flag per evitare rientro circolare

        self.hotkey_mgr = HotkeyManager(self)
        self._connetti_azioni()
        self._connetti_listener_clipboard()
        self.hotkey_mgr.setup_hotkeys()

        logging.info("[LOG-MANAGER] PADAS Clipboard Manager avviato con successo e in ascolto.")

    def carica_sessione_automatica(self):
        """Carica automaticamente l'ultimo export salvato all'avvio."""
        path_target = getattr(self, "percorso_autosalvataggio", Path("padas_clipboard_export.json"))
        
        if path_target and Path(path_target).exists():
            logging.info(f"[LOG-MANAGER] Trovata sessione precedente in {path_target}. Caricamento in corso...")
            ok = ClipboardIO.carica_autosalvataggio_silenzioso(self, self.memoria, self._refresh, target_path=path_target)
            if not ok:
                QMessageBox.warning(
                    self,
                    "Errore Caricamento Sessione",
                    f"Impossibile ripristinare i dati dall'ultimo salvataggio automatico:\n{path_target}\n\n"
                    "Il file potrebbe essere danneggiato o non formattato correttamente."
                )

        if hasattr(super(), "carica_sessione_automatica"):
            super().carica_sessione_automatica()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _refresh(self):
        """Richiama l'aggiornamento della tabella nella GUI."""
        self.refresh_table(self.memoria, self.elementi_massivi)

    def toggle_window(self):
        """Mostra o nasconde la finestra principale aggiornandola[cite: 2]."""
        if self.isVisible():
            self.hide()
        else:
            self._refresh()
            self.show()
            self.activateWindow()

    def closeEvent(self, event):
        """Salva i dati della sessione prima di chiudere."""
        if self.memoria or self.elementi_massivi:
            reply = QMessageBox.question(
                self, 'Salvataggio Sessione',
                'Vuoi salvare i dati della sessione prima di uscire?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if reply == QMessageBox.StandardButton.Yes:
                path_target = getattr(self, "percorso_autosalvataggio", None)
                ClipboardIO.save_to_json(self, self.memoria, self.elementi_massivi, target_path=path_target)

        event.accept()
        QApplication.quit()

