"""
PADAS CLIPBOARD MANAGER - GUI DIALOGS MIXIN
Gestisce i metodi di supporto per le azioni di dialogo e le operazioni di svuotamento/eliminazione righe.
"""


class GUIDialogsMixin:
    """Mixin per la gestione delle operazioni di dialogo e manipolazione delle selezioni multiple."""

    def svuota_righe_selezionate(self, rows: list):
        """Interfaccia per lo svuotamento del contenuto delle righe selezionate (sovrascritta dal manager)."""
        pass

    def elimina_righe_selezionate(self, rows: list):
        """Interfaccia per l'eliminazione completa delle righe selezionate (sovrascritta dal manager)."""
        pass

