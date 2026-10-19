# python applicazioni\multi_copia\main.py
"""
PADAS CLIPBOARD MANAGER (MODALITÀ DIRETTA SENZA POP-UP - VERSIONE PyQt6)
 • Shift + Alt + Z poi [Tasto Slot] -> Copia e assegna subito allo slot
 • Shift + Alt + X poi [Tasto Slot] -> Prendi da Ctrl+C e assegna subito
 • Shift + Alt + F poi [Tasto Slot] -> Copia Formato Selettivo (con Pannello Spunte)
 • Shift + Alt + G poi [Slot Preset] poi [Slot Memoria] -> Applica Preset al volo
 • Shift + Alt + S                  -> Mostra/Nascondi la tabella
 • Shift + Alt + D poi [Slot Preset] -> Incolla
 • Shift + Alt + W, Q, E = cacenlla tutti i dati non bloccati
 - shift + Alt + W + slot = cancella quello speicfico slot
 - Shift + Alt + Q -> Blocca/Sblocca Slot
 - Shift + Alt + E + [Slot 1] + [Slot 2] -> Incolla Multiplo (da Slot 1 a Slot 2)
 - Shift + Alt + A + [Slot 1] + {numero colonne}
 - shift + Alt + M + [Slot 1] + {Slot 2} -> Crea File Multipli (da Slot 1 a Slot 2)
 - Shift + Alt + E = incollo su google drive l'ultimo screnshoot (ma solo il link)
 - Shift + Alt + R = incolla multiplo a coordinate
"""
# NOTE: {} = dati falcoltativi

import sys
import signal
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from clipboard import PadasClipboardManager

# ------------------------------------------------------------------------------
# PERCORSI SALVATAGGIO LOCALE AUTOMATICO CONFIGURAZIONI E MEMORIA
# ------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PERCORSO_CONFIG_TASTIERA = BASE_DIR / "configurazione_tastiera.json"
PERCORSO_MEMORIA_EXPORT = BASE_DIR / "padas_clipboard_export.json"


def setup_logging():
    """Configura il logging di sistema per mostrare tutti i messaggi [LOG-...] direttamente nel terminale."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def setup_signal_handling():
    """Consente di interrompere l'applicazione da terminale tramite Ctrl+C (SIGINT)."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    setup_logging()
    setup_signal_handling()
    
    logging.info("[MAIN] Avvio PADAS Clipboard Manager con tracciamento log attivo...")

    app = QApplication(sys.argv)
    app.setApplicationName("PADAS DevStudio - Clipboard Memory Manager")

    manager = PadasClipboardManager()
    
    # Assegnazione dei percorsi locali riservati al modulo
    if PERCORSO_MEMORIA_EXPORT:
        manager.percorso_autosalvataggio = Path(PERCORSO_MEMORIA_EXPORT)

    if PERCORSO_CONFIG_TASTIERA and hasattr(manager, "keyboard_map"):
        manager.keyboard_map.config_file_path = Path(PERCORSO_CONFIG_TASTIERA)
        manager.keyboard_map.config = manager.keyboard_map._carica_configurazione()
        manager.keyboard_map.init_ui()

    # Ripristino automatico dell'ultima sessione all'avvio
    manager.carica_sessione_automatica()

    manager.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()