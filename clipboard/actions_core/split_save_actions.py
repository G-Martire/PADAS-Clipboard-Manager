"""
PADAS CLIPBOARD MANAGER - SPLIT & SAVE ACTIONS
Logica operativa per la suddivisione del testo della clipboard e la distribuzione sugli slot.
"""

import logging
import winsound
from PyQt6.QtWidgets import QApplication, QMessageBox
from .text_splitter import TextSplitterHelper
from .keyboard_grid import KeyboardGridHelper


class SplitSaveActionsManager:
    """Gestisce l'operazione Split & Save (Copia Multipla) tramite composizione."""

    def __init__(self, manager):
        self.manager = manager  # Riceve il riferimento al Manager principale

    def split_and_save_dati(self, slot_inizio: str, param2: str, memoria: list, elementi_massivi: list, layout_matrice: list, config_split: dict, refresh_callback, parent_widget=None):
        """Esegue l'operazione Split & Save (Copia Multipla): suddivide il testo della clipboard e lo distribuisce sugli slot."""
        logging.info(f"[SPLIT-SAVE] Avvio Split & Save da Slot '{slot_inizio.upper()}' con Param2 '{param2.upper()}'...")
        clipboard = QApplication.clipboard()
        testo_puro = clipboard.text() if clipboard.mimeData().hasText() else ""

        if not testo_puro:
            logging.warning("[SPLIT-SAVE] Clipboard vuota o priva di testo.")
            return

        separatore = TextSplitterHelper.rileva_separatore(testo_puro, config_split)
        elementi = TextSplitterHelper.splitta_testo(testo_puro, separatore)

        if not elementi:
            logging.warning("[SPLIT-SAVE] Nessun elemento ricavato dallo split del testo.")
            return

        sequenza_slot = KeyboardGridHelper.calcola_sequenza_slot(slot_inizio, param2, layout_matrice, config_split)
        
        gestione_occupati = config_split.get("gestione_occupati", "trasla")
        slot_salvati = 0
        slot_bloccati_saltati = 0
        overflow_massivo = 0

        idx_slot = 0
        for elem in elementi:
            slot_target = None
            while idx_slot < len(sequenza_slot):
                candidato = sequenza_slot[idx_slot]
                idx_slot += 1

                # Controllo se lo slot è BLOCCATO (🔒)
                item_esistente = next((e for e in memoria if e.get("slot") == candidato), None)
                if item_esistente and item_esistente.get("bloccato", False):
                    slot_bloccati_saltati += 1
                    logging.info(f"[SPLIT-SAVE] Slot '{candidato.upper()}' BLOCCATO (🔒): saltato.")
                    continue

                slot_target = candidato
                break

            if slot_target:
                item_occupato = next((e for e in memoria if e.get("slot") == slot_target), None)
                if item_occupato:
                    if gestione_occupati == "trasla":
                        self._trasla_elemento_successivo(item_occupato, sequenza_slot, idx_slot, memoria, elementi_massivi)
                    else:
                        memoria.remove(item_occupato)

                nuovo_id = max([item.get("id", 0) for item in memoria], default=0) + 1
                nuovo_item = {
                    "id": nuovo_id,
                    "slot": slot_target,
                    "tipo": "Testo",
                    "dato": elem,
                    "html": "",
                    "anteprima": elem.replace("\n", " ")[:50],
                    "note": "Split & Save"
                }
                memoria.append(nuovo_item)
                slot_salvati += 1
            else:
                elementi_massivi.append({
                    "tipo": "Testo",
                    "dato": elem,
                    "html": "",
                    "anteprima": elem.replace("\n", " ")[:50],
                    "note": "Overflow Split & Save"
                })
                overflow_massivo += 1

        refresh_callback()

        try:
            winsound.Beep(800, 150)
        except Exception:
            pass

        msg = f"<b>Split & Save Completato!</b><br><br>" \
              f"• Elementi distribuiti negli slot: <b>{slot_salvati}</b><br>"
        if slot_bloccati_saltati > 0:
            msg += f"• Slot protetti (🔒) saltati: <b>{slot_bloccati_saltati}</b><br>"
        if overflow_massivo > 0:
            msg += f"• Elementi salvati in Cattura Massiva (senza slot): <b>{overflow_massivo}</b><br>"

        if parent_widget and (slot_bloccati_saltati > 0 or overflow_massivo > 0 or config_split.get("mostra_anteprima", True)):
            QMessageBox.information(parent_widget, "Riepilogo Split & Save", msg)

    def _trasla_elemento_successivo(self, item_da_traslare, sequenza_slot, start_idx, memoria, elementi_massivi):
        """Sposta un elemento occupato nello slot libero successivo o in cattura massiva."""
        for idx in range(start_idx, len(sequenza_slot)):
            s_cand = sequenza_slot[idx]
            i_exist = next((e for e in memoria if e.get("slot") == s_cand), None)
            if not i_exist:
                item_da_traslare["slot"] = s_cand
                logging.info(f"[SPLIT-SAVE] Traslato vecchio elemento nello slot '{s_cand.upper()}'.")
                return

        memoria.remove(item_da_traslare)
        elementi_massivi.append({
            "tipo": item_da_traslare.get("tipo", "Testo"),
            "dato": item_da_traslare.get("dato", ""),
            "html": item_da_traslare.get("html", ""),
            "anteprima": item_da_traslare.get("anteprima", ""),
            "note": "Traslato da Split & Save"
        })

