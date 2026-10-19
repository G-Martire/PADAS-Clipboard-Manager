"""
PADAS CLIPBOARD MANAGER - GUI MENUS MIXIN
Gestisce la creazione della barra dei menu superiore e della toolbar dei comandi rapidi.
"""

from PyQt6.QtWidgets import QMenuBar, QMenu, QHBoxLayout, QPushButton
from PyQt6.QtGui import QAction


class GUIMenusMixin:
    """Mixin per la gestione dei menu e della toolbar della GUI."""

    def _costruisci_menu_e_toolbar(self, frame_layout):
        # ------------------------------------------------------------------
        # RIGA 2: BARRA DEI MENU SUPERIORE
        # ------------------------------------------------------------------
        menu_bar = QMenuBar(self)

        menu_file = menu_bar.addMenu("File")
        menu_importa = QMenu("Importa", self)
        
        self.act_import_json = QAction("Importa da JSON...", self)
        menu_importa.addAction(self.act_import_json)

        self.act_import_excel = QAction("Importa da Excel (.xlsx, .xls)...", self)
        menu_importa.addAction(self.act_import_excel)

        self.act_import_csv = QAction("Importa da CSV...", self)
        menu_importa.addAction(self.act_import_csv)

        menu_file.addMenu(menu_importa)
        menu_file.addSeparator()

        # Esportazioni: Rapida vs Guidata
        self.act_export_rapido = QAction("Esporta Rapido (Sostituisce file locale)", self)
        menu_file.addAction(self.act_export_rapido)

        self.act_export_custom = QAction("Esporta con nome / Scegli cartella...", self)
        menu_file.addAction(self.act_export_custom)

        menu_file.addSeparator()

        self.act_svuota = QAction("Svuota Tabella / Memoria", self)
        menu_file.addAction(self.act_svuota)

        menu_strumenti = menu_bar.addMenu("Strumenti")
        self.act_opzioni_notifica = QAction("Opzioni Notifiche...", self)
        menu_strumenti.addAction(self.act_opzioni_notifica)

        self.act_config_split_save = QAction("Configura Split & Save...", self)
        menu_strumenti.addAction(self.act_config_split_save)

        menu_guida = menu_bar.addMenu("Guida")
        self.act_scorciatoie = QAction("Legenda Scorciatoie Rapide", self)
        menu_guida.addAction(self.act_scorciatoie)

        frame_layout.addWidget(menu_bar)

        # ------------------------------------------------------------------
        # RIGA 3: TOOLBAR COMPATTA SUPERIORE
        # ------------------------------------------------------------------
        toolbar_layout = QHBoxLayout()

        self.btn_massiva = QPushButton("Cattura Massiva: OFF")
        self.btn_massiva.setCheckable(True)
        toolbar_layout.addWidget(self.btn_massiva)

        self.btn_toggle_path = QPushButton("Vista File: Solo Nome")
        self.btn_toggle_path.setCheckable(True)
        self.btn_toggle_path.setToolTip("Alterna tra la visualizzazione del percorso completo e il solo nome dei file")
        toolbar_layout.addWidget(self.btn_toggle_path)

        self.btn_lock_selected = QPushButton("🔒 Blocca/Sblocca Selezionati")
        self.btn_lock_selected.setToolTip("Blocca o sblocca tutte le righe selezionate nella tabella")
        toolbar_layout.addWidget(self.btn_lock_selected)

        self.btn_toggle_keyboard = QPushButton("⌨ Mappa Tastiera")
        self.btn_toggle_keyboard.setCheckable(True)
        self.btn_toggle_keyboard.setChecked(True)
        self.btn_toggle_keyboard.setToolTip("Mostra o nasconde la mappa visiva della tastiera affiancata")
        toolbar_layout.addWidget(self.btn_toggle_keyboard)

        self.btn_help = QPushButton("Legenda Scorciatoie (Shift + Alt)")
        toolbar_layout.addWidget(self.btn_help)

        self.btn_split_save_config = QPushButton("✂️ Configura Split & Save")
        self.btn_split_save_config.setToolTip("Personalizza le regole di estrazione e salvataggio per la Copia Multipla")
        toolbar_layout.addWidget(self.btn_split_save_config)

        toolbar_layout.addStretch()
        frame_layout.addLayout(toolbar_layout)


