"""
PADAS CLIPBOARD MANAGER - INPUT/OUTPUT E IMPORT/EXPORT
Contiene le funzioni per il caricamento e il salvataggio dei dati (JSON, CSV, Excel).
"""

import json
import csv
import logging
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QFileDialog

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ClipboardIO:
    """Gestisce tutte le operazioni di I/O per memoria ed elementi massivi."""

    @staticmethod
    def import_json(parent_widget, memoria: list, refresh_callback):
        """Importa gli slot da un file JSON supportando sia la struttura a Lista che a Dizionario."""
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Seleziona file JSON da importare", "", "JSON (*.json)"
        )
        if not file_path:
            return

        try:
            with open(Path(file_path), "r", encoding="utf-8") as f:
                data = json.load(f)

            elementi_importati = 0

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        slot_clean = str(item.get("slot", "")).strip().lower()
                        item_sanificato = {
                            "id": item.get("id", max([e.get("id", 0) for e in memoria], default=0) + 1),
                            "slot": slot_clean,
                            "tipo": item.get("tipo", "Testo"),
                            "dato": item.get("dato", ""),
                            "html": item.get("html", ""),
                            "anteprima": item.get("anteprima", str(item.get("dato", ""))[:50]),
                            "note": item.get("note", ""),
                            "bloccato": bool(item.get("bloccato", False))
                        }
                        
                        idx_esistente = next((i for i, e in enumerate(memoria) if e.get("slot") == slot_clean and slot_clean != ""), None)
                        if idx_esistente is not None:
                            memoria[idx_esistente] = item_sanificato
                        else:
                            memoria.append(item_sanificato)
                        
                        elementi_importati += 1

            elif isinstance(data, dict):
                for k, v in data.items():
                    slot_clean = str(k).strip().lower()
                    if isinstance(v, dict):
                        item_sanificato = {
                            "id": v.get("id", max([e.get("id", 0) for e in memoria], default=0) + 1),
                            "slot": slot_clean,
                            "tipo": v.get("tipo", "Testo"),
                            "dato": v.get("dato", ""),
                            "html": v.get("html", ""),
                            "anteprima": v.get("anteprima", str(v.get("dato", ""))[:50]),
                            "note": v.get("note", ""),
                            "bloccato": bool(v.get("bloccato", False))
                        }
                        idx_esistente = next((i for i, e in enumerate(memoria) if e.get("slot") == slot_clean and slot_clean != ""), None)
                        if idx_esistente is not None:
                            memoria[idx_esistente] = item_sanificato
                        else:
                            memoria.append(item_sanificato)
                        elementi_importati += 1

            refresh_callback()
            logging.info(f"[LOG-IO] Importati con successo {elementi_importati} elementi dal file JSON.")
            QMessageBox.information(parent_widget, "Successo", f"Importati {elementi_importati} slot da JSON correttamente.")

        except Exception as e:
            logging.error(f"[LOG-IO] Errore nell'importazione del file JSON: {e}")
            QMessageBox.critical(parent_widget, "Errore Importazione", f"Impossibile leggere il file JSON:\n{e}")

    @staticmethod
    def import_excel(parent_widget, memoria: list, elementi_massivi: list, refresh_callback):
        """Importa gli slot o la cattura massiva da un file Excel (.xlsx, .xls)."""
        if not PANDAS_AVAILABLE:
            QMessageBox.warning(
                parent_widget, "Libreria Mancante",
                "Per importare file Excel è necessario installare 'pandas' e 'openpyxl'.\n"
                "Puoi installarli dal terminale con: pip install pandas openpyxl"
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Seleziona file Excel da importare", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            ClipboardIO._importa_da_dataframe(df, memoria, elementi_massivi)
            refresh_callback()
            QMessageBox.information(parent_widget, "Successo", "Dati importati da Excel correttamente.")
        except Exception as e:
            QMessageBox.critical(parent_widget, "Errore Importazione", f"Impossibile leggere il file Excel:\n{e}")

    @staticmethod
    def import_csv(parent_widget, memoria: list, elementi_massivi: list, refresh_callback):
        """Importa gli slot o la cattura massiva da un file CSV."""
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Seleziona file CSV da importare", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            with open(Path(file_path), mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    slot = row.get("Slot", "").strip().lower()
                    tipo = row.get("Tipo Dato", "Testo")
                    dato = row.get("Contenuto", row.get("Contenuto / Anteprima", ""))
                    note = row.get("Note", "")

                    item = {
                        "id": max([e.get("id", 0) for e in memoria], default=0) + 1,
                        "slot": slot,
                        "tipo": tipo,
                        "dato": dato,
                        "html": "",
                        "anteprima": dato.replace("\n", " ")[:50],
                        "note": note,
                        "bloccato": False
                    }

                    if slot and len(slot) == 1:
                        idx_esistente = next((i for i, e in enumerate(memoria) if e.get("slot") == slot), None)
                        if idx_esistente is not None:
                            memoria[idx_esistente] = item
                        else:
                            memoria.append(item)
                    else:
                        elementi_massivi.append(item)

            refresh_callback()
            QMessageBox.information(parent_widget, "Successo", "Dati importati da CSV correttamente.")
        except Exception as e:
            QMessageBox.critical(parent_widget, "Errore Importazione", f"Impossibile leggere il file CSV:\n{e}")

    @staticmethod
    def _importa_da_dataframe(df, memoria: list, elementi_massivi: list):
        """Helper interno per la conversione dei DataFrame pandas."""
        for _, row in df.iterrows():
            slot = str(row.get("Slot", "")).strip().lower() if "Slot" in row else ""
            tipo = str(row.get("Tipo Dato", "Testo")) if "Tipo Dato" in row else "Testo"
            dato = str(row.get("Contenuto", row.get("Contenuto / Anteprima", "")))
            note = str(row.get("Note", "")) if "Note" in row and not pd.isna(row["Note"]) else ""

            item = {
                "id": max([e.get("id", 0) for e in memoria], default=0) + 1,
                "slot": slot,
                "tipo": tipo,
                "dato": dato,
                "html": "",
                "anteprima": dato.replace("\n", " ")[:50],
                "note": note,
                "bloccato": False
            }

            if slot and len(slot) == 1 and slot != "nan":
                idx_esistente = next((i for i, e in enumerate(memoria) if e.get("slot") == slot), None)
                if idx_esistente is not None:
                    memoria[idx_esistente] = item
                else:
                    memoria.append(item)
            else:
                elementi_massivi.append(item)

    @staticmethod
    def save_to_json(parent_widget, memoria: list, elementi_massivi: list, target_path=None):
        """Salva automaticamente la memoria corrente nel file locale specificato."""
        if not memoria and not elementi_massivi:
            return

        path = Path(target_path) if target_path else Path("padas_clipboard_export.json")
        try:
            dati_da_salvare = list(memoria) + list(elementi_massivi)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dati_da_salvare, f, indent=4, ensure_ascii=False)
            logging.info(f"[LOG-IO] Autosalvataggio memoria eseguito in: {path.resolve()}")
        except Exception as e:
            logging.error(f"[LOG-IO] Errore durante l'autosalvataggio in JSON: {e}")

    @staticmethod
    def export_as_json(parent_widget, memoria: list, elementi_massivi: list):
        """Apre un dialogo di salvataggio per esportare la memoria in un file e percorso a scelta dell'utente."""
        if not memoria and not elementi_massivi:
            QMessageBox.information(parent_widget, "Info", "La memoria è vuota! Nessun dato da esportare.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Esporta Memoria in JSON",
            "padas_clipboard_export.json",
            "JSON (*.json)"
        )
        if not file_path:
            return

        try:
            dati_da_salvare = list(memoria) + list(elementi_massivi)
            with open(Path(file_path), "w", encoding="utf-8") as f:
                json.dump(dati_da_salvare, f, indent=4, ensure_ascii=False)
            logging.info(f"[LOG-IO] Memoria esportata con successo in: {file_path}")
            QMessageBox.information(parent_widget, "Esportazione Completata", f"Dati esportati con successo in:\n{file_path}")
        except Exception as e:
            logging.error(f"[LOG-IO] Errore nell'esportazione guidata JSON: {e}")
            QMessageBox.critical(parent_widget, "Errore Esportazione", f"Impossibile esportare il file:\n{e}")

    @staticmethod
    def carica_autosalvataggio_silenzioso(parent_widget, memoria: list, refresh_callback, target_path=None) -> bool:
        """Carica la sessione in background all'avvio. Restituisce True se va a buon fine, False se fallisce."""
        path = Path(target_path) if target_path else Path("padas_clipboard_export.json")
        if not path.exists():
            return True

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        slot_clean = str(item.get("slot", "")).strip().lower()
                        item_sanificato = {
                            "id": item.get("id", max([e.get("id", 0) for e in memoria], default=0) + 1),
                            "slot": slot_clean,
                            "tipo": item.get("tipo", "Testo"),
                            "dato": item.get("dato", ""),
                            "html": item.get("html", ""),
                            "anteprima": item.get("anteprima", str(item.get("dato", ""))[:50]),
                            "note": item.get("note", ""),
                            "bloccato": bool(item.get("bloccato", False))
                        }
                        memoria.append(item_sanificato)

            refresh_callback()
            logging.info(f"[LOG-IO] Ripristinati {len(memoria)} slot dall'autosalvataggio iniziale.")
            return True

        except Exception as e:
            logging.error(f"[LOG-IO] Errore durante il caricamento automatico della sessione: {e}")
            return False

