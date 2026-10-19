"""
PADAS CLIPBOARD MANAGER - HOTKEY A MACCHINA A STATI CON SEGNALI THREAD-SAFE
Supporto per Shift+Alt+Z / A / D / E / R / W / Q / X / F / G / M.
"""

import time
import logging
import keyboard
from PyQt6.QtWidgets import QApplication
from .signals import signals


class HotkeyManager:
    """Gestisce l'intercettazione condizionale e il sequenziamento della tastiera."""

    def __init__(self, manager_instance):
        self.mgr = manager_instance
        self.in_ascolto_slot = False
        self.hook_globale = None

    def setup_hotkeys(self):
        """Inizializza la macchina a stati e collega i segnali."""
        signals.show_gui.connect(self.mgr.toggle_window)
        signals.trigger_from_clipboard.connect(self.mgr.salva_da_clipboard_sistema)
        signals.trigger_copy_format.connect(self.mgr.copia_formato_selettivo)
        signals.trigger_apply_preset.connect(self.mgr.applica_preset_formato)
        signals.trigger_paste_slot.connect(self.mgr.esegui_incollo_da_segnale)
        signals.trigger_multi_paste_slot.connect(self.mgr.esegui_incollo_multiplo_da_segnale)
        signals.trigger_save_slot.connect(self.mgr.esegui_salvataggio_da_segnale)
        signals.trigger_split_save_slot.connect(self.mgr.esegui_split_save_da_segnale)
        signals.trigger_create_files_slot.connect(self.mgr.esegui_creazione_file_da_segnale)
        signals.trigger_drive_image_upload.connect(self.mgr.esegui_upload_drive_da_segnale)
        signals.trigger_clear_slot.connect(self.mgr.esegui_cancellazione_da_segnale)
        signals.trigger_toggle_lock.connect(self.mgr.esegui_toggle_blocco_da_segnale)

        logging.info("[HOTKEY] Inizializzazione Macchina a Stati (Shift+Alt+Z / A / D / E / R / W / Q / M)...")
        self.hook_globale = keyboard.hook(self._gestore_stato_tastiera, suppress=False)

    def _gestore_stato_tastiera(self, event):
        """Macchina a stati: intercetta Alt con Shift per innescare le sequenze di comando."""
        key_name = event.name.lower() if event.name else ""

        if event.event_type == 'down':
            if key_name in ['alt', 'left alt', 'right alt', 'alt gr']:
                shift_reale = (
                    keyboard.is_pressed('shift') or 
                    keyboard.is_pressed('left shift') or 
                    keyboard.is_pressed('right shift')
                )
                
                if shift_reale and not self.in_ascolto_slot:
                    logging.info("[LOG-HOTKEY] Premuto Alt con Shift FISICAMENTE ATTIVO -> Sequenza Shift+Alt RILEVATA!")
                    self.in_ascolto_slot = True
                    keyboard.call_later(self._intercetta_e_gestisci_slot, delay=0.01)

    def _intercetta_e_gestisci_slot(self):
        """Cattura il comando (Z, A, D, E, R, Q, W, S, X, F, G, M) premuto subito dopo Shift + Alt."""
        tasto_comando = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)

        if tasto_comando:
            logging.info(f"[LOG-HOTKEY] Comando '{tasto_comando.upper()}' riconosciuto dopo Shift + Alt.")
            
            if tasto_comando == 'z':
                logging.info("[LOG-HOTKEY] Shift + Alt + Z confermato -> Invio copia selezione e ascolto Tasto Slot...")
                self.rilascia_tasti_modifica()
                keyboard.send('ctrl+c')
                time.sleep(0.05)
                
                tasto_slot = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                if tasto_slot:
                    logging.info(f"[LOG-HOTKEY] Slot '{tasto_slot.upper()}' intercettato per SALVATAGGIO...")
                    signals.trigger_save_slot.emit(tasto_slot)

            elif tasto_comando == 'a':
                logging.info("[LOG-HOTKEY] Shift + Alt + A confermato -> Invio copia selezione e ascolto Slot Inizio (Split & Save)...")
                self.rilascia_tasti_modifica()
                keyboard.send('ctrl+c')
                time.sleep(0.05)
                
                slot_inizio = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                if slot_inizio:
                    secondo_tasto = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                    param2 = secondo_tasto if secondo_tasto else ""
                    logging.info(f"[LOG-HOTKEY] Split & Save: Slot Inizio '{slot_inizio.upper()}', Param2 '{param2.upper()}'")
                    signals.trigger_split_save_slot.emit(slot_inizio, param2)

            elif tasto_comando == 'm':
                logging.info("[LOG-HOTKEY] Shift + Alt + M confermato -> In ascolto dello Slot / Coordinate per CREAZIONE FILE...")
                slot_inizio = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                if slot_inizio:
                    secondo_tasto = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                    param2 = secondo_tasto if secondo_tasto else ""
                    logging.info(f"[LOG-HOTKEY] Creazione File: Slot Inizio '{slot_inizio.upper()}', Param2 '{param2.upper()}'")
                    signals.trigger_create_files_slot.emit(slot_inizio, param2)

            elif tasto_comando == 'e':
                logging.info("[LOG-HOTKEY] Shift + Alt + E confermato -> Esecuzione Upload Immagine su Drive e copia Link...")
                self.rilascia_tasti_modifica()
                signals.trigger_drive_image_upload.emit()

            elif tasto_comando == 'r':
                logging.info("[LOG-HOTKEY] Shift + Alt + R confermato -> In ascolto delle COORDINATE (Slot Inizio e Fine)...")
                slot_inizio = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                if slot_inizio:
                    slot_fine = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                    if not slot_fine:
                        slot_fine = slot_inizio
                    logging.info(f"[LOG-HOTKEY] Coordinate '{slot_inizio.upper()}' -> '{slot_fine.upper()}' intercettate per INCOLLO MULTIPLO...")
                    signals.trigger_multi_paste_slot.emit(slot_inizio, slot_fine)

            elif tasto_comando == 'd':
                logging.info("[LOG-HOTKEY] Shift + Alt + D confermato -> In ascolto dello Slot da INCOLLARE...")
                tasto_slot = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                if tasto_slot:
                    logging.info(f"[LOG-HOTKEY] Slot '{tasto_slot.upper()}' intercettato per INCOLLO...")
                    signals.trigger_paste_slot.emit(tasto_slot)

            elif tasto_comando == 'q':
                logging.info("[LOG-HOTKEY] Shift + Alt + Q confermato -> In ascolto dello Slot da BLOCCARE/SBLOCCARE...")
                tasto_slot = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                if tasto_slot:
                    signals.trigger_toggle_lock.emit(tasto_slot)

            elif tasto_comando == 'w':
                logging.info("[LOG-HOTKEY] Shift + Alt + W confermato -> In ascolto della sequenza di CANCELLAZIONE...")
                primo_tasto = self.cattura_singolo_tasto_invisibile(timeout_sec=1.5)
                if primo_tasto:
                    if primo_tasto == 'q':
                        secondo_tasto = self.cattura_singolo_tasto_invisibile(timeout_sec=0.35)
                        if secondo_tasto == 'e':
                            signals.trigger_clear_slot.emit('__ALL__')
                        else:
                            signals.trigger_clear_slot.emit('q')
                    else:
                        signals.trigger_clear_slot.emit(primo_tasto)

            elif tasto_comando == 's':
                signals.show_gui.emit()
            elif tasto_comando == 'x':
                signals.trigger_from_clipboard.emit()
            elif tasto_comando == 'f':
                signals.trigger_copy_format.emit()
            elif tasto_comando == 'g':
                signals.trigger_apply_preset.emit()
        else:
            logging.warning("[LOG-HOTKEY] Timeout o nessun tasto valido premuto dopo Shift + Alt.")

        self.reset_sicurezza_tastiera()

    @staticmethod
    def rilascia_tasti_modifica():
        """Rilascio sicuro dei modificatori."""
        tasti = ['shift', 'left shift', 'right shift', 'ctrl', 'left ctrl', 'right ctrl', 'windows', 'alt', 'left alt', 'right alt', 'alt gr']
        for k in tasti:
            try:
                if keyboard.is_pressed(k):
                    keyboard.release(k)
            except Exception:
                pass

    def reset_sicurezza_tastiera(self):
        """Ripristina lo stato neutro della tastiera."""
        self.in_ascolto_slot = False
        self.rilascia_tasti_modifica()

    def cattura_singolo_tasto_invisibile(self, timeout_sec=1.5):
        """Sequestra temporaneamente il solo tasto dello Slot."""
        tasto_catturato = []
        tasti_esclusi = [
            'alt', 'left alt', 'right alt', 'alt gr',
            'ctrl', 'left ctrl', 'right ctrl',
            'shift', 'left shift', 'right shift', 'maiusc',
            'windows', 'left windows', 'right windows',
            'tab', 'esc', 'escape', 'enter', 'invio', 'backspace'
        ]

        def _blocco_slot(event):
            if event.event_type == 'down':
                tasto = event.name.lower() if event.name else ""
                if tasto not in tasti_esclusi and len(tasto) == 1:
                    logging.info(f"[LOG-CATTURA] Tasto singolo intercettato: '{tasto.upper()}'")
                    tasto_catturato.append(tasto)

        self.rilascia_tasti_modifica()
        hook_temp = keyboard.hook(_blocco_slot, suppress=True)

        start_time = time.time()
        while not tasto_catturato and (time.time() - start_time < timeout_sec):
            QApplication.processEvents()
            time.sleep(0.01)

        try:
            keyboard.unhook(hook_temp)
        except Exception:
            pass

        return tasto_catturato[0] if tasto_catturato else None

