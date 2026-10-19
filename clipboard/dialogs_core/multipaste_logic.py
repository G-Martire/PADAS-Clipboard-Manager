"""
PADAS CLIPBOARD MANAGER - DIALOGS CORE
Logica di calcolo, assemblaggio del testo e aggiornamento anteprima per l'incollo multiplo.
"""

import re


class MultiPasteLogicMixin:
    """Mixin contenente la logica di calcolo e assemblaggio del testo per MultiPasteOptionsDialog."""

    def get_testo_assemblato(self) -> str:
        direzione_base = self.get_direzione_base()
        sep = self.get_separatore()

        # Ordinamento principale degli slot compresi nelle coordinate
        elementi = list(self.slot_trovati)
        if direzione_base == "verticale":
            elementi.sort(key=lambda x: (x.get("colonna", 0), x.get("riga", 0)))
        else:
            elementi.sort(key=lambda x: (x.get("riga", 0), x.get("colonna", 0)))

        blocco_slots_unito = sep.join([item.get("dato", "") for item in elementi if item.get("dato")])

        # Se la personalizzazione multilinea è attiva
        if self.chk_custom_dir.isChecked() and self.txt_custom_order.toPlainText().strip():
            raw_text = self.txt_custom_order.toPlainText()
            
            # 1. Gestione segnaposto {SLOTS}
            if "{SLOTS}" in raw_text:
                risultato = raw_text.replace("{SLOTS}", blocco_slots_unito)
            else:
                # 2. Parsing per token, slot singoli e stringhe tra virgolette
                tokens = re.findall(r'"([^"]*)"|([^\s,\n]+)', raw_text)
                parti = []
                for t_literal, t_slot in tokens:
                    if t_literal:
                        parti.append(t_literal)
                    elif t_slot:
                        s_clean = t_slot.strip().lower()
                        # Se il token è esplicitamente \n inseriamo un andata a capo
                        if s_clean == "\\n":
                            parti.append("\n")
                        else:
                            item = next((e for e in self.slot_trovati if e.get("slot", "").strip().lower() == s_clean), None)
                            if item and item.get("dato"):
                                parti.append(item.get("dato"))
                risultato = sep.join(parti) if parti else raw_text

            # Convertiamo eventuali sequenze \n scritte nel testo generico in vere andate a capo
            return risultato.replace("\\n", "\n")

        return blocco_slots_unito

    def _aggiorna_anteprima(self):
        direzione_base = self.get_direzione_base()
        self.preview_matrix_widget.aggiorna_modalita(direzione_base)
        self.txt_preview.setPlainText(self.get_testo_assemblato())

    def get_struttura_personalizzata(self) -> str:
        """Restituisce il testo multilinea della struttura personalizzata."""
        return self.txt_custom_order.toPlainText()

    def is_custom_dir_attivo(self) -> bool:
        """Restituisce True se la casella di personalizzazione è spuntata."""
        return self.chk_custom_dir.isChecked()

