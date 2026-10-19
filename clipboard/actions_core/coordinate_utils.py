"""
PADAS CLIPBOARD MANAGER - COORDINATE UTILS
Modulo di supporto per il calcolo geometrico dei range e delle coordinate sulla matrice.
"""

import logging


class CoordinateUtils:
    """Gestisce il calcolo geometrico delle coordinate e dei range tra slot tramite composizione."""

    def __init__(self, manager):
        self.manager = manager  # Riceve il riferimento al Manager principale

    @staticmethod
    def calcola_range_coordinate(slot_start: str, slot_end: str, layout_matrice: list) -> tuple:
        """Calcola gli slot compresi nel rettangolo/intervallo tra slot_start e slot_end."""
        start_clean = slot_start.strip().lower()
        end_clean = slot_end.strip().lower()

        pos_start = None
        pos_end = None

        for r_idx, riga in enumerate(layout_matrice):
            for c_idx, val in enumerate(riga):
                v_clean = str(val).strip().lower()
                if v_clean == start_clean:
                    pos_start = (r_idx, c_idx)
                if v_clean == end_clean:
                    pos_end = (r_idx, c_idx)

        if not pos_start or not pos_end:
            if pos_start:
                return ([{"slot": start_clean, "riga": pos_start[0], "colonna": pos_start[1]}], 1)
            return ([], 0)

        r_min, r_max = min(pos_start[0], pos_end[0]), max(pos_start[0], pos_end[0])
        c_min, c_max = min(pos_start[1], pos_end[1]), max(pos_start[1], pos_end[1])

        slot_dettagli = []
        totale_area = 0

        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                if c < len(layout_matrice[r]):
                    totale_area += 1
                    slot_name = str(layout_matrice[r][c]).strip().lower()
                    slot_dettagli.append({
                        "slot": slot_name,
                        "riga": r,
                        "colonna": c
                    })

        return (slot_dettagli, totale_area)

