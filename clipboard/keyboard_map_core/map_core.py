"""
PADAS CLIPBOARD MANAGER - KEYBOARD MAP CORE
Gestisce l'inizializzazione, il caricamento/salvataggio JSON e la costruzione delle matrici di layout[cite: 1].
"""

import os
import json
import logging
from pathlib import Path
from PyQt6.QtCore import pyqtSignal
from .config_dialog import KeyboardConfigDialog


class KeyboardMapCoreMixin:
    """Mixin per la gestione della configurazione e dei layout della tastiera[cite: 1]."""
    
    slot_selected = pyqtSignal(str)
    DEFAULT_CONFIG_NAME = "configurazione_tastiera.json"

    def _inizializza_core_mappa(self, config_path=None):
        self.tasti_map = {}
        self.edit_mode = False

        if config_path:
            self.config_file_path = Path(config_path)
        else:
            self.config_file_path = Path(os.getcwd()) / self.DEFAULT_CONFIG_NAME

        self.config = self._carica_configurazione()

    def _carica_configurazione(self) -> dict:
        if self.config_file_path.exists():
            try:
                with open(self.config_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Errore nel caricamento della tastiera da {self.config_file_path}: {e}")
        return {
            "preset_name": "Italiana Standard (ISO)",
            "custom_keys": "",
            "custom_layout_matrix": None
        }

    def _salva_configurazione(self):
        try:
            self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info(f"[LOG-CONFIG] Tastiera salvata in: {self.config_file_path}")
        except Exception as e:
            logging.error(f"Errore nel salvataggio della tastiera in {self.config_file_path}: {e}")

    def _costruisci_layout_corrente(self) -> list:
        custom_matrix = self.config.get("custom_layout_matrix")
        if custom_matrix:
            return custom_matrix

        preset_nome = self.config.get("preset_name", "Italiana Standard (ISO)")
        layout_base = KeyboardConfigDialog.PRESETS.get(
            preset_nome, 
            KeyboardConfigDialog.PRESETS["Italiana Standard (ISO)"]
        )

        matrice_finale = [list(riga) for riga in layout_base]

        custom_raw = self.config.get("custom_keys", "")
        if custom_raw:
            tasti_extra = [k.strip().lower() for k in custom_raw.split(",") if k.strip()]
            if tasti_extra:
                matrice_finale.append(tasti_extra)

        return matrice_finale

