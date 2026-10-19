"""
PADAS CLIPBOARD MANAGER - KEYBOARD MAP ACTIONS
Gestisce le azioni interattive, il Drag & Drop tra righe, lo scambio dei tasti e l'aggiornamento della mappa.
"""

from PyQt6.QtCore import Qt
from .config_dialog import KeyboardConfigDialog


class KeyboardMapActionsMixin:
    """Mixin per la gestione delle azioni, Drag & Drop e aggiornamento della mappa[cite: 1]."""

    def dragEnterEvent(self, event):
        if self.edit_mode and event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if not self.edit_mode or not event.mimeData().hasText():
            return

        slot_trascinato = event.mimeData().text().lower()
        pos_drop = event.position().toPoint()

        riga_destinazione_idx = 0
        min_distanza_y = float('inf')

        for idx, r_layout in enumerate(self.righe_layouts):
            rect_riga = r_layout.geometry()
            centro_y = rect_riga.center().y()
            distanza = abs(pos_drop.y() - centro_y)
            if distanza < min_distanza_y:
                min_distanza_y = distanza
                riga_destinazione_idx = idx

        self._sposta_tasto_in_coda_riga(slot_trascinato, riga_destinazione_idx)
        event.acceptProposedAction()

    def _sposta_tasto_in_coda_riga(self, slot_id: str, target_row_idx: int):
        matrice = self._costruisci_layout_corrente()

        tasto_trovato = None
        for riga in matrice:
            if slot_id in riga:
                riga.remove(slot_id)
                tasto_trovato = slot_id
                break

        if not tasto_trovato:
            return

        if target_row_idx >= len(matrice):
            matrice.append([tasto_trovato])
        else:
            matrice[target_row_idx].append(tasto_trovato)

        matrice = [r for r in matrice if len(r) > 0]

        self.config["custom_layout_matrix"] = matrice
        self._salva_configurazione()
        self.init_ui()

        main_window = self.window()
        if hasattr(main_window, "memoria"):
            self.aggiorna_mappa(main_window.memoria)

    def toggle_edit_mode(self):
        self.edit_mode = self.btn_edit_mode.isChecked()
        self._aggiorna_stile_btn_edit()
        for btn in self.tasti_map.values():
            btn.set_edit_mode(self.edit_mode)

    def _scambia_posizioni_tasti(self, slot_src: str, slot_dst: str):
        matrice = self._costruisci_layout_corrente()
        
        pos_src = None
        pos_dst = None

        for r_idx, riga in enumerate(matrice):
            for c_idx, val in enumerate(riga):
                if val.lower() == slot_src.lower():
                    pos_src = (r_idx, c_idx)
                if val.lower() == slot_dst.lower():
                    pos_dst = (r_idx, c_idx)

        if pos_src and pos_dst:
            r1, c1 = pos_src
            r2, c2 = pos_dst
            matrice[r1][c1], matrice[r2][c2] = matrice[r2][c2], matrice[r1][c1]

            self.config["custom_layout_matrix"] = matrice
            self._salva_configurazione()
            self.init_ui()
            
            main_window = self.window()
            if hasattr(main_window, "memoria"):
                self.aggiorna_mappa(main_window.memoria)

    def apri_dialogo_configurazione(self):
        dlg = KeyboardConfigDialog(self.config, parent=self)
        if dlg.exec():
            nuova_config = dlg.get_config()
            nuova_config["custom_layout_matrix"] = None
            self.config = nuova_config
            
            self._salva_configurazione()
            self.init_ui()
            
            main_window = self.window()
            if hasattr(main_window, "memoria"):
                self.aggiorna_mappa(main_window.memoria)

    def aggiorna_mappa(self, memoria: list):
        stati_slot = {}
        for item in memoria:
            slot = item.get("slot", "").strip().lower()
            if slot:
                stati_slot[slot] = {
                    "occupied": True,
                    "locked": item.get("bloccato", False)
                }

        for slot_id, btn_widget in self.tasti_map.items():
            info = stati_slot.get(slot_id, {"occupied": False, "locked": False})
            btn_widget.aggiorna_stato(occupied=info["occupied"], locked=info["locked"])

