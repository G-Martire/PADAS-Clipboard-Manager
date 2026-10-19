"""
PADAS CLIPBOARD MANAGER - SELECTIVE FORMAT ACTIONS
Gestione dell'estrazione di formato selettivo (HTML/stili) dalla clipboard.
"""

import logging
from PyQt6.QtWidgets import QApplication


class SelectiveFormatManager:
    """Gestisce l'estrazione del formato selettivo tramite composizione."""

    SEGNAPOSTO_SOLO_STILE = "__PADAS_STYLE_ONLY__"

    def __init__(self, manager):
        self.manager = manager  # Riceve il riferimento al Manager principale

    def estrai_formato_selettivo(self, tasto_slot: str, memoria: list, filtri: dict, refresh_callback):
        """Estrae l'HTML filtrando le proprietà."""
        logging.info(f"[LOG-ACTION] Estrazione Formato Selettivo per lo Slot '{tasto_slot.upper()}'...")
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if not (mime_data.hasHtml() or mime_data.hasText()):
            logging.warning("[LOG-ACTION] Nessun formato o testo trovato nella clipboard.")
            return

        html_data = mime_data.html() if mime_data.hasHtml() else f"<span>{mime_data.text()}</span>"
        testo_puro = mime_data.text() if mime_data.hasText() else ""
        
        mantiene_testo = filtri.get("text", False) or filtri.get("font", True) or filtri.get("bold_italic", True)
        
        if not mantiene_testo:
            dato_salvato = self.SEGNAPOSTO_SOLO_STILE
            tipo_descr = "Solo Stile"
            anteprima_str = "[Solo Stile / Convenzione]"
        else:
            dato_salvato = testo_puro
            is_tabella = "<table>" in html_data.lower() or "\t" in testo_puro
            tipo_descr = "Stile + Tabella" if is_tabella else "Stile + Testo"
            anteprima_str = f"[{tipo_descr}] {testo_puro.replace('\n', ' ')[:40]}"

        nuovo_id = max([item.get("id", 0) for item in memoria], default=0) + 1
        slot_clean = tasto_slot.strip().lower()

        nuovo_elemento = {
            "id": nuovo_id,
            "slot": slot_clean,
            "tipo": tipo_descr,
            "dato": dato_salvato,
            "html": html_data,
            "filtri": filtri,
            "anteprima": anteprima_str,
            "note": ""
        }

        memoria.append(nuovo_elemento)
        refresh_callback()

