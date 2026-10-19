"""
PADAS CLIPBOARD MANAGER - TEXT SPLITTER
Utility statiche per il rilevamento del separatore e il parsing dei testi per Split & Save.
"""

import logging


class TextSplitterHelper:
    """Utility statiche per il rilevamento del separatore e il parsing dei testi per Split & Save."""

    GERARCHIA_SEPARATORI = ["\n", ";", ",", ".", "-", "|"]

    @classmethod
    def rileva_separatore(cls, testo: str, config: dict) -> str:
        """Rileva automaticamente il separatore in base alla gerarchia o alla configurazione dell'utente."""
        if not testo:
            return "\n"

        # 1. Controllo se il separatore è definito nella prima parte/riga del testo
        if config.get("separatore_definito_in_testo", True):
            prima_riga = testo.splitlines()[0] if testo.splitlines() else testo
            for sep in [";", ",", "|", "\t"]:
                if sep in prima_riga and prima_riga.count(sep) >= 1:
                    logging.info(f"[SPLIT-HELPER] Rilevato separatore nell'intestazione/prima riga: '{sep}'")
                    return sep

        # 2. Separatore esplicito impostato nelle opzioni
        sep_config = config.get("separatore_default", "auto")
        if sep_config == "custom" and config.get("separatore_custom"):
            return config.get("separatore_custom")
        elif sep_config != "auto":
            return sep_config

        # 3. Fallback: ricerca gerarchica automatica
        for sep in cls.GERARCHIA_SEPARATORI:
            if sep in testo:
                logging.info(f"[SPLIT-HELPER] Rilevato separatore gerarchico di fallback: '{repr(sep)}'")
                return sep

        return "\n"

    @classmethod
    def splitta_testo(cls, testo: str, separatore: str) -> list[str]:
        """Pulisce e suddivide il testo in base al separatore individuato."""
        if not testo:
            return []

        if separatore == "\n":
            elementi = testo.splitlines()
        else:
            elementi = testo.split(separatore)

        elementi_puliti = [elem.strip() for elem in elementi if elem.strip()]
        logging.info(f"[SPLIT-HELPER] Testo suddiviso in {len(elementi_puliti)} elementi con separatore '{repr(separatore)}'")
        return elementi_puliti

    @classmethod
    def rileva_elementi_file(cls, testo: str) -> list[str]:
        """
        Verifica se il testo nello slot contiene separatori di lista (es: virgole, punto e virgola, a capo, pipe)
        ed estrae i singoli elementi escludendo il punto '.' usato per le estensioni.
        """
        if not testo:
            return []

        for sep in ["\n", ";", ",", "|"]:
            if sep in testo:
                elementi = [elem.strip() for elem in testo.split(sep) if elem.strip()]
                if len(elementi) > 1:
                    return elementi

        return [testo.strip()] if testo.strip() else []

