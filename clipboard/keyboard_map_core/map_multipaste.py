"""
PADAS CLIPBOARD MANAGER - KEYBOARD MAP MULTIPASTE
Gestisce la configurazione e l'apertura del dialogo per l'incollo multiplo.
"""

import logging


class KeyboardMapMultipasteMixin:
    """Mixin per la gestione dell'Incollo Multiplo associato alla mappa tastiera[cite: 1]."""

    def apri_configurazione_incollo_multiplo(self):
        """Apre il dialogo di configurazione dell'Incollo Multiplo e consente di riabilitare l'anteprima[cite: 1]."""
        from ..dialogs_core import MultiPasteOptionsDialog
        from ..actions_core import ClipboardActions

        main_window = self.window()
        memoria = getattr(main_window, "memoria", [])

        slot_1 = memoria[0].get("slot", "1") if memoria else "1"
        slot_2 = memoria[-1].get("slot", "E") if memoria else "E"

        layout_matrice = self._costruisci_layout_corrente()
        slot_dettagli, totale_area = ClipboardActions.calcola_range_coordinate(slot_1, slot_2, layout_matrice)

        elementi_trovati = []
        for dett in slot_dettagli:
            s_name = dett["slot"]
            item = next((e for e in memoria if e.get("slot", "").strip().lower() == s_name), None)
            if item and item.get("dato"):
                item_copy = dict(item)
                item_copy["riga"] = dett["riga"]
                item_copy["colonna"] = dett["colonna"]
                elementi_trovati.append(item_copy)

        dlg = MultiPasteOptionsDialog(
            slot_inizio=slot_1,
            slot_fine=slot_2,
            slot_trovati=elementi_trovati,
            totali_area=totale_area,
            parent=main_window
        )
        
        mostra_anteprima = self.config.get("mostra_anteprima_multi_paste", True)
        is_custom = self.config.get("custom_dir_attivo", False)
        struttura_salvata = self.config.get("struttura_personalizzata", "")

        dlg.chk_skip_preview.setChecked(not mostra_anteprima)
        dlg.chk_custom_dir.setChecked(is_custom)
        if struttura_salvata:
            dlg.txt_custom_order.setPlainText(struttura_salvata)

        if dlg.exec():
            separatore_scelto = dlg.get_separatore()
            direzione_scelta = dlg.get_direzione()
            disattiva_in_futuro = dlg.deve_disattivare_anteprima()

            self.config["mostra_anteprima_multi_paste"] = not disattiva_in_futuro
            self.config["separatore_multi_paste"] = separatore_scelto
            self.config["direzione_multi_paste"] = direzione_scelta
            self.config["custom_dir_attivo"] = dlg.is_custom_dir_attivo()
            self.config["struttura_personalizzata"] = dlg.get_struttura_personalizzata()
            self._salva_configurazione()
            logging.info(f"[LOG-CONFIG] Impostazioni incollo multiplo aggiornate: Anteprima={not disattiva_in_futuro}, Custom={dlg.is_custom_dir_attivo()}")


