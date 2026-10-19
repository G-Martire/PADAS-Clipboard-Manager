"""
PADAS CLIPBOARD MANAGER - GUI CORE MIXIN
Gestisce l'inizializzazione della finestra, la palette colori, gli eventi di tastiera e il ridimensionamento/trascinamento della finestra frameless.
"""

import logging
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QPalette, QColor, QKeyEvent


class GUICoreMixin:
    """Mixin per la gestione del nucleo centrale della finestra principale (GUI)."""

    MARGIN_SIZE = 6  # Margine esatto in pixel per l'attivazione del bordo resize

    def _inizializza_core_gui(self):
        self.old_pos = None
        self.resizing_edge = None
        self._applica_palette_python()

    def _applica_palette_python(self):
        """Palette 'Soft Mint / Verde Salvia Chiaro' con evidenziatore azzurro tenue."""
        palette = QPalette()

        # Sfondo principale della finestra (Verde Salvia Molto Chiaro)
        palette.setColor(QPalette.ColorRole.Window, QColor(232, 245, 233))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(27, 67, 50))

        # Tabella e campi editabili (Menta Chiaro e Righe Alternate)
        palette.setColor(QPalette.ColorRole.Base, QColor(241, 248, 233))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(220, 237, 219))
        palette.setColor(QPalette.ColorRole.Text, QColor(27, 67, 50))

        # Pulsanti e componenti (Verde Polvere / Salvia Medio)
        palette.setColor(QPalette.ColorRole.Button, QColor(200, 230, 201))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(27, 67, 50))

        # Evidenziatore / Selezione (Azzurro Chiaro Pastello + Testo Scuro)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(187, 222, 251))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(27, 67, 50))

        self.setPalette(palette)

    def keyPressEvent(self, event):
        """Gestisce le scorciatoie Canc (svuota) e Backspace (elimina righe) per tutte le righe selezionate."""
        key = event.key()
        
        if key in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace]:
            selected_rows = list(set(index.row() for index in self.table.selectedIndexes()))
            logging.info(f"[LOG-GUI-KEY] Tasto rilevato: {key} | Righe Selezionate: {selected_rows}")

            if selected_rows:
                if key == Qt.Key.Key_Delete:
                    logging.info("[LOG-GUI-KEY] Esecuzione svuota_righe_selezionate (CANC)...")
                    if hasattr(self, "svuota_righe_selezionate"):
                        self.svuota_righe_selezionate(selected_rows)
                    return
                elif key == Qt.Key.Key_Backspace:
                    logging.info("[LOG-GUI-KEY] Esecuzione elimina_righe_selezionate (BACKSPACE)...")
                    if hasattr(self, "elimina_righe_selezionate"):
                        self.elimina_righe_selezionate(selected_rows)
                    return

        super().keyPressEvent(event)

    def changeEvent(self, event: QEvent):
        """Intercetta la richiesta di minimizzazione dalla barra applicazioni di Windows."""
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                event.accept()
        super().changeEvent(event)

    def _calcola_bordo(self, pos: QPoint):
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        m = self.MARGIN_SIZE

        top = y <= m
        bottom = y >= h - m
        left = x <= m
        right = x >= w - m

        if top and left: return 'top-left'
        if top and right: return 'top-right'
        if bottom and left: return 'bottom-left'
        if bottom and right: return 'bottom-right'
        if top: return 'top'
        if bottom: return 'bottom'
        if left: return 'left'
        if right: return 'right'
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            self.resizing_edge = self._calcola_bordo(pos)
            
            if not self.resizing_edge and self.title_bar_container.geometry().contains(pos):
                self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()

        if not event.buttons():
            edge = self._calcola_bordo(pos)
            if edge in ['top-left', 'bottom-right']: 
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif edge in ['top-right', 'bottom-left']: 
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif edge in ['top', 'bottom']: 
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif edge in ['left', 'right']: 
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else: 
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        if self.resizing_edge:
            global_pos = event.globalPosition().toPoint()
            rect = self.geometry()

            if 'right' in self.resizing_edge: rect.setRight(global_pos.x())
            if 'bottom' in self.resizing_edge: rect.setBottom(global_pos.y())
            if 'left' in self.resizing_edge: rect.setLeft(global_pos.x())
            if 'top' in self.resizing_edge: rect.setTop(global_pos.y())

            if rect.width() >= self.minimumWidth() and rect.height() >= self.minimumHeight():
                self.setGeometry(rect)
            return

        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.resizing_edge = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

