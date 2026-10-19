"""
PADAS CLIPBOARD MANAGER - LOCK & CLEAR OPERATIONS MIXIN
Gestisce il blocco (🔒), lo sblocco e le cancellazioni sicure degli slot.
"""

import logging
import winsound
from PyQt6.QtWidgets import QMessageBox


class LockClearOperationsMixin:
    """Mixin per la gestione dei blocchi e delle cancellazioni degli slot."""

    def esegui_toggle_blocco_da_segnale(self, tasto_slot: str):
        """Riceve lo slot via segnale PyQt6 ed esegue il toggle del blocco."""
        if not tasto_slot:
            return
            
        slot_clean = tasto_slot.strip().lower()
        item = next((e for e in self.memoria if e.get("slot") == slot_clean), None)

        if item:
            stato_attuale = item.get("bloccato", False)
            item["bloccato"] = not stato_attuale
            nuovo_stato = item["bloccato"]

            if nuovo_stato:
                logging.info(f"[LOG-MANAGER] Slot '{slot_clean.upper()}' BLOCCATO con successo (🔒).")
                try:
                    winsound.Beep(1200, 150)
                except Exception:
                    pass
            else:
                logging.info(f"[LOG-MANAGER] Slot '{slot_clean.upper()}' SBLOCCATO con successo (🔓).")
                try:
                    winsound.Beep(700, 150)
                except Exception:
                    pass

            self._refresh()
        else:
            logging.warning(f"[LOG-MANAGER] Impossibile bloccare: Lo slot '{slot_clean.upper()}' è VUOTO o non esiste!")
            try:
                winsound.Beep(300, 200)
            except Exception:
                pass

    def esegui_cancellazione_da_segnale(self, bersaglio: str):
        """Riceve la richiesta di cancellazione mantenendo intatti gli slot BLOCCATI (🔒)."""
        if bersaglio == '__ALL__':
            logging.info("[LOG-MANAGER] Ricevuto segnale Thread-Safe per CANCELLAZIONE TOTALE (Rispettando i blocchi)...")
            self.memoria = [e for e in self.memoria if e.get("bloccato", False)]
            self.elementi_massivi.clear()
            self._refresh()
            try:
                winsound.Beep(400, 200)
            except Exception:
                pass
        else:
            slot_clean = bersaglio.strip().lower()
            logging.info(f"[LOG-MANAGER] Ricevuto segnale Thread-Safe per CANCELLAZIONE dello Slot '{slot_clean.upper()}'.")
            
            item = next((e for e in self.memoria if e.get("slot") == slot_clean), None)
            
            if item:
                if item.get("bloccato", False):
                    logging.warning(f"[LOG-MANAGER] Cancellazione respinta: Lo slot '{slot_clean.upper()}' è BLOCCATO (🔒)!")
                    try:
                        winsound.Beep(300, 250)
                    except Exception:
                        pass
                    QMessageBox.warning(
                        self,
                        "Slot Bloccato",
                        f"Lo Slot '{slot_clean.upper()}' è BLOCCATO (🔒) e non può essere cancellato!\n\n"
                        f"Sbloccalo prima con 'Shift + Alt + Q' seguito da '{slot_clean.upper()}'."
                    )
                else:
                    self.memoria = [e for e in self.memoria if e.get("slot") != slot_clean]
                    self._refresh()
                    logging.info(f"[LOG-MANAGER] Slot '{slot_clean.upper()}' svuotato con successo!")
                    try:
                        winsound.Beep(800, 100)
                    except Exception:
                        pass
            else:
                logging.warning(f"[LOG-MANAGER] Impossibile cancellare: Slot '{slot_clean.upper()}' non trovato o già vuoto.")

    def toggle_blocco_selezionati(self):
        """Applica la logica Smart di blocco/sblocco a tutte le righe selezionate."""
        selected_indexes = self.table.selectedIndexes()
        if not selected_indexes:
            logging.warning("[LOG-MANAGER] Nessuna riga selezionata per il blocco/sblocco.")
            return

        selected_rows = sorted(list(set(index.row() for index in selected_indexes)))
        
        elementi_target = []
        for row in selected_rows:
            if row < len(self.memoria):
                elementi_target.append(self.memoria[row])

        if not elementi_target:
            logging.warning("[LOG-MANAGER] Nessun elemento di memoria valido trovato nelle righe selezionate.")
            return

        almeno_uno_sbloccato = any(not item.get("bloccato", False) for item in elementi_target)
        nuovo_stato = almeno_uno_sbloccato

        for item in elementi_target:
            item["bloccato"] = nuovo_stato

        azione_str = "BLOCCATE" if nuovo_stato else "SBLOCCATE"
        logging.info(f"[LOG-MANAGER] {len(elementi_target)} righe {azione_str} con successo!")

        try:
            freq = 1200 if nuovo_stato else 700
            winsound.Beep(freq, 150)
        except Exception:
            pass

        self._refresh()

    def clear_memory(self):
        """Svuota la tabella e la memoria mantenendo gli slot bloccati."""
        if not self.memoria and not self.elementi_massivi:
            return

        reply = QMessageBox.question(
            self, 'Conferma Svuotamento',
            'Sei sicuro di voler svuotare tutta la tabella e la memoria degli slot?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.memoria = [e for e in self.memoria if e.get("bloccato", False)]
            self.elementi_massivi.clear()
            self._refresh()

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

