"""
PADAS CLIPBOARD MANAGER - MULTI PASTE ACTIONS
Gestione dell'incollo multiplo coordinato tra due slot, inclusa l'interazione con l'anteprima.
"""

import time
import ctypes
import logging
import keyboard
from PyQt6.QtWidgets import QApplication
from .coordinate_utils import CoordinateUtils


class MultiPasteActionsManager:
    """Gestisce l'incollo multiplo coordinato tramite composizione."""

    def __init__(self, manager):
        self.manager = manager  # Riceve il riferimento al Manager principale

    def incolla_multiplo_coordinate(self, slot_start: str, slot_end: str, memoria: list, layout_matrice: list, callback_release_keys, parent_widget=None):
        """Esegue l'incollo multiplo tra due coordinate."""
        user32 = ctypes.windll.user32
        hwnd_target = user32.GetForegroundWindow()

        slot_dettagli, totale_area = CoordinateUtils.calcola_range_coordinate(slot_start, slot_end, layout_matrice)
        
        elementi_trovati = []
        for dett in slot_dettagli:
            s_name = dett["slot"]
            item = next((e for e in memoria if e.get("slot", "").strip().lower() == s_name), None)
            if item and item.get("dato"):
                item_copy = dict(item)
                item_copy["riga"] = dett["riga"]
                item_copy["colonna"] = dett["colonna"]
                elementi_trovati.append(item_copy)

        if not elementi_trovati:
            logging.warning(f"[LOG-ACTIONS] Nessun dato trovato nell'intervallo {slot_start.upper()} -> {slot_end.upper()}")
            return

        config_map = getattr(parent_widget, "keyboard_map", None) if parent_widget else None
        mostra_anteprima = True
        separatore_default = "\n"
        direzione_default = "orizzontale"

        if config_map and hasattr(config_map, "config"):
            mostra_anteprima = config_map.config.get("mostra_anteprima_multi_paste", True)
            separatore_default = config_map.config.get("separatore_multi_paste", "\n")
            direzione_default = config_map.config.get("direzione_multi_paste", "orizzontale")

        testo_finale = ""

        if mostra_anteprima:
            from ..dialogs_core import MultiPasteOptionsDialog
            dlg = MultiPasteOptionsDialog(
                slot_inizio=slot_start,
                slot_fine=slot_end,
                slot_trovati=elementi_trovati,
                totali_area=totale_area,
                parent=parent_widget
            )
            
            if config_map and hasattr(config_map, "config"):
                is_custom = config_map.config.get("custom_dir_attivo", False)
                struttura_salvata = config_map.config.get("struttura_personalizzata", "")
                
                dlg.chk_custom_dir.setChecked(is_custom)
                if struttura_salvata:
                    dlg.txt_custom_order.setPlainText(struttura_salvata)

            if dlg.exec():
                testo_finale = dlg.get_testo_assemblato()
                separatore_scelto = dlg.get_separatore()
                direzione_scelta = dlg.get_direzione()
                disattiva_in_futuro = dlg.deve_disattivare_anteprima()

                if config_map and hasattr(config_map, "config"):
                    if disattiva_in_futuro:
                        config_map.config["mostra_anteprima_multi_paste"] = False
                    config_map.config["separatore_multi_paste"] = separatore_scelto
                    config_map.config["direzione_multi_paste"] = direzione_scelta
                    config_map.config["custom_dir_attivo"] = dlg.is_custom_dir_attivo()
                    config_map.config["struttura_personalizzata"] = dlg.get_struttura_personalizzata()
                    config_map._salva_configurazione()
            else:
                return
        else:
            if direzione_default == "verticale":
                elementi_trovati.sort(key=lambda x: (x.get("colonna", 0), x.get("riga", 0)))
            else:
                elementi_trovati.sort(key=lambda x: (x.get("riga", 0), x.get("colonna", 0)))

            testi = [item.get("dato", "") for item in elementi_trovati if item.get("dato")]
            testo_finale = separatore_default.join(testi)

        if testo_finale:
            callback_release_keys()
            QApplication.clipboard().setText(testo_finale)

            if hwnd_target:
                user32.SetForegroundWindow(hwnd_target)
                time.sleep(0.1)

            keyboard.send('ctrl+v')
            logging.info(f"[LOG-ACTIONS] Incollo multiplo eseguito per l'intervallo {slot_start.upper()} -> {slot_end.upper()}")

