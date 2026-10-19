"""
PADAS CLIPBOARD MANAGER - KEYBOARD GRID HELPER
Utility statiche per la generazione della sequenza ordinata di slot sulla matrice reale della tastiera.
"""


class KeyboardGridHelper:
    """Utility statiche per la generazione della sequenza ordinata di slot sulla matrice reale della tastiera."""

    @classmethod
    def calcola_sequenza_slot(cls, slot_start: str, param2: str, layout_matrice: list, config: dict) -> list[str]:
        """
        Genera la lista ordinata degli slot di destinazione a partire dallo slot iniziale:
        - ORIZZONTALE: Avanza per colonne (sinistra -> destra), scendendo verticalmente per N righe per ciascuna colonna.
        - VERTICALE: Avanza per righe (alto -> basso), scorrendo orizzontalmente per N colonne per ciascuna riga.
        """
        start_clean = slot_start.strip().lower()
        param2_clean = param2.strip().lower() if param2 else ""

        n_val = config.get("colonne_default", 4)
        direzione = config.get("direzione_default", "orizzontale")

        if param2_clean.isdigit():
            n_val = int(param2_clean)

        if not layout_matrice:
            return [start_clean]

        # 1. Trova la posizione di partenza nella matrice (riga, colonna)
        pos_start = None
        for r_idx, riga in enumerate(layout_matrice):
            for c_idx, val in enumerate(riga):
                if str(val).strip().lower() == start_clean:
                    pos_start = (r_idx, c_idx)
                    break
            if pos_start:
                break

        if not pos_start:
            return [start_clean]

        r_start, c_start = pos_start
        sequenza = []
        max_righe = len(layout_matrice)
        max_colonne = max(len(r) for r in layout_matrice) if layout_matrice else 0

        # 2. Generazione sequenza in base al flusso selezionato
        if direzione == "orizzontale":
            # Avanzamento Orizzontale (per Colonne): per ogni colonna da c_start a max_colonne,
            # scende per N righe a partire da r_start (o da riga 0 per le colonne successive)
            for c_idx in range(c_start, max_colonne):
                r_inizio = r_start if c_idx == c_start else 0
                r_fine = min(r_inizio + n_val, max_righe)
                for r_idx in range(r_inizio, r_fine):
                    if c_idx < len(layout_matrice[r_idx]):
                        slot_name = str(layout_matrice[r_idx][c_idx]).strip().lower()
                        if slot_name and slot_name not in sequenza:
                            sequenza.append(slot_name)
        else:
            # Avanzamento Verticale (per Righe): per ogni riga da r_start a max_righe,
            # scorre per N colonne a partire da c_start (o da colonna 0 per le righe successive)
            for r_idx in range(r_start, max_righe):
                riga = layout_matrice[r_idx]
                c_inizio = c_start if r_idx == r_start else 0
                c_fine = min(c_inizio + n_val, len(riga))
                for c_idx in range(c_inizio, c_fine):
                    slot_name = str(riga[c_idx]).strip().lower()
                    if slot_name and slot_name not in sequenza:
                        sequenza.append(slot_name)

        return sequenza

