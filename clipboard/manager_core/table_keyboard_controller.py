"""
PADAS CLIPBOARD MANAGER - TABLE & KEYBOARD CONTROLLER MIXIN
Gestisce la modifica delle celle in tabella, l'interazione con la mappa tastiera virtuale e la cancellazione/svuotamento righe.
"""

import logging
from PyQt6.QtWidgets import QMessageBox


class TableKeyboardControllerMixin:
    """Mixin per la gestione della tabella e dei controller da tastiera/mappa."""

    def _on_cell_changed(self, row, column):
        """Gestisce la modifica diretta delle celle."""
        slot_item = self.table.item(row, 0)
        
        if column == 0:
            if not slot_item:
                return

            nuovo_slot = slot_item.text().strip().lower()

            if not nuovo_slot or len(nuovo_slot) != 1:
                self._refresh()
                return

            duplicato_presente = any(item.get("slot") == nuovo_slot for i, item in enumerate(self.memoria) if i != row)

            if row < len(self.memoria):
                slot_vecchio = self.memoria[row].get("slot", "")
                if slot_vecchio != nuovo_slot:
                    if duplicato_presente:
                        QMessageBox.warning(
                            self,
                            "Slot Duplicato",
                            f"Attenzione: Lo slot '{nuovo_slot.upper()}' è già assegnato a un'altra riga!\n"
                            "Entrambe le righe rimarranno salvate e verranno evidenziate per evitare conflitti."
                        )

                    self.memoria[row]["slot"] = nuovo_slot
                    logging.info(f"[LOG-MANAGER] Riga {row} (ID {self.memoria[row].get('id')}): slot aggiornato da '{slot_vecchio.upper()}' a '{nuovo_slot.upper()}'.")
                self._refresh()

            else:
                idx_massivo = row - len(self.memoria)
                if 0 <= idx_massivo < len(self.elementi_massivi):
                    if duplicato_presente:
                        QMessageBox.warning(
                            self,
                            "Slot Duplicato",
                            f"Attenzione: Lo slot '{nuovo_slot.upper()}' è già assegnato a un'altra riga!\n"
                            "L'elemento è stato promosso ma verrà evidenziato come duplicato."
                        )

                    item = self.elementi_massivi.pop(idx_massivo)
                    nuovo_id = max([e.get("id", 0) for e in self.memoria], default=0) + 1
                    item["id"] = nuovo_id
                    item["slot"] = nuovo_slot
                    self.memoria.append(item)
                    logging.info(f"[LOG-MANAGER] Elemento massivo promosso a Slot '{nuovo_slot.upper()}' (ID {nuovo_id}).")
                self._refresh()

        elif column == 3:
            note_item = self.table.item(row, 3)
            if note_item and row < len(self.memoria):
                self.memoria[row]["note"] = note_item.text()

    def svuota_righe_selezionate(self, rows: list):
        """Tasto CANC: Svuota il contenuto delle righe selezionate rispettando gli slot BLOCCATI (🔒)."""
        righe_svuotate = 0
        for row in rows:
            if row < len(self.memoria):
                item = self.memoria[row]
                if item.get("bloccato", False):
                    logging.warning(f"[LOG-MANAGER] Riga {row} non svuotata perché lo slot '{item.get('slot', '').upper()}' è BLOCCATO (🔒).")
                    continue

                self.memoria[row]["dato"] = ""
                self.memoria[row]["html"] = ""
                self.memoria[row]["anteprima"] = "[Svuotato]"
                self.memoria[row]["tipo"] = "Vuoto"
                righe_svuotate += 1
            else:
                idx_massivo = row - len(self.memoria)
                if 0 <= idx_massivo < len(self.elementi_massivi):
                    self.elementi_massivi[idx_massivo]["dato"] = ""
                    self.elementi_massivi[idx_massivo]["html"] = ""
                    self.elementi_massivi[idx_massivo]["anteprima"] = "[Svuotato]"
                    self.elementi_massivi[idx_massivo]["tipo"] = "Vuoto"
                    righe_svuotate += 1
        
        logging.info(f"[LOG-MANAGER] Svuotate {righe_svuotate} righe con il tasto CANC.")
        self._refresh()

    def elimina_righe_selezionate(self, rows: list):
        """Tasto BACKSPACE: Elimina interamente le righe selezionate rispettando gli slot BLOCCATI (🔒)."""
        righe_eliminate = 0
        # Ordinamento decrescente obbligatorio per non alterare gli indici durante i pop()
        for row in sorted(rows, reverse=True):
            if row < len(self.memoria):
                item = self.memoria[row]
                if item.get("bloccato", False):
                    logging.warning(f"[LOG-MANAGER] Riga {row} non eliminata perché lo slot '{item.get('slot', '').upper()}' è BLOCCATO (🔒).")
                    continue

                rimosso = self.memoria.pop(row)
                righe_eliminate += 1
                logging.info(f"[LOG-MANAGER] Riga {row} (ID {rimosso.get('id')}) eliminata con BACKSPACE.")
            else:
                idx_massivo = row - len(self.memoria)
                if 0 <= idx_massivo < len(self.elementi_massivi):
                    self.elementi_massivi.pop(idx_massivo)
                    righe_eliminate += 1
                    logging.info(f"[LOG-MANAGER] Riga massiva {idx_massivo} eliminata con BACKSPACE.")
        
        if righe_eliminate > 0:
            self._refresh()

    def _seleziona_riga_da_slot(self, slot_id: str):
        """Seleziona la riga corrispondente in tabella quando l'utente clicca un tasto sulla mappa visiva."""
        slot_clean = slot_id.strip().lower()
        for row in range(len(self.memoria)):
            item = self.memoria[row]
            if item.get("slot", "").strip().lower() == slot_clean:
                self.table.selectRow(row)
                self.table.scrollToItem(self.table.item(row, 0))
                logging.info(f"[LOG-MANAGER] Cliccato tasto mappa '{slot_clean.upper()}': riga {row} selezionata in tabella.")
                return

