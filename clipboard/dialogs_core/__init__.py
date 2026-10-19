"""
PADAS CLIPBOARD MANAGER - DIALOGS CORE
Package initialization per i dialoghi e le finestre di configurazione.
"""

from .format_filter import FormatoFilterDialog
from .notifications import OpzioniNotificheDialog
from .matrix_preview import MatrixPreviewWidget
from .multipaste_options import MultiPasteOptionsDialog
from .split_save_config import SplitSaveConfigDialog
from .make_files_dialog import MakeFilesOptionsDialog

__all__ = [
    "FormatoFilterDialog",
    "OpzioniNotificheDialog",
    "MatrixPreviewWidget",
    "MultiPasteOptionsDialog",
    "SplitSaveConfigDialog",
    "MakeFilesOptionsDialog"
]

