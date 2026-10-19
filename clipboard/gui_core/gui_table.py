"""
PADAS CLIPBOARD MANAGER - GUI TABLE MIXIN
Gestisce il delegato personalizzato SlotItemDelegate, la tabella principale e il metodo di aggiornamento dati.
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QStyledItemDelegate,
    QLineEdit, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor, QKeyEvent


class SlotItemDelegate(QStyledItemDelegate):
    """Delegato personalizzato per la colonna Slot (Colonna 0)."""

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setMaxLength(1)
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return editor

    def eventFilter(self, editor, event):
        if event.type() == QEvent.Type.KeyPress:
            key_event: QKeyEvent = event
            key = key_event.key()
            modifiers = key_event.modifiers()

            tasti_navigazione = [
                Qt.Key.Key_Backspace, Qt.Key.Key_Delete,
                Qt.Key.Key_Return, Qt.Key.Key_Enter,
                Qt.Key.Key_Escape, Qt.Key.Key_Tab
            ]
            if key in tasti_navigazione:
                return super().eventFilter(editor, event)

            if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12 or key in [Qt.Key.Key_Meta, Qt.Key.Key_CapsLock]:
                return True

            if (modifiers & Qt.KeyboardModifier.ShiftModifier) or (modifiers & Qt.KeyboardModifier.GroupSwitchModifier):
                return True

            text = key_event.text()
            if not text or len(text) != 1:
                return True

        return super().eventFilter(editor, event)


class GUITableMixin:
    """Mixin per la gestione della tabella dati e della mappa tastiera affiancata[cite: 2]."""

    def _costruisci_tabella_e_mappa(self, frame_layout):
        content_layout = QHBoxLayout()

        self.table = QTableWidget(0, 4)
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(["Slot", "Tipo Dato", "Contenuto / Anteprima", "Note"])
        self.table.setWordWrap(True)
        self.table.setItemDelegateForColumn(0, SlotItemDelegate())

        # Intercettiamo i tasti CANC e BACKSPACE anche se premuti direttamente dentro la QTableWidget
        original_key_press = self.table.keyPressEvent
        def table_key_press_override(event):
            if event.key() in [Qt.Key.Key_Delete, Qt.Key.Key_Backspace]:
                # Inoltriamo l'evento alla finestra principale (gui_core)
                self.keyPressEvent(event)
            else:
                original_key_press(event)

        self.table.keyPressEvent = table_key_press_override

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        content_layout.addWidget(self.table)

        from ..keyboard_map_core import KeyboardMapWidget
        self.keyboard_map = KeyboardMapWidget(self)
        content_layout.addWidget(self.keyboard_map)

        frame_layout.addLayout(content_layout)

    def refresh_table(self, memoria: list, elementi_massivi: list):
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        solo_nome_file = not getattr(self, "mostra_percorso_completo", False)

        PALETTE_DUPLICATI = [
            QColor(255, 205, 210), QColor(255, 224, 178),
            QColor(225, 190, 231), QColor(179, 229, 252), QColor(255, 245, 157)
        ]

        conteggio_slot = {}
        for item in memoria:
            s = item.get("slot", "").strip().lower()
            if s:
                conteggio_slot[s] = conteggio_slot.get(s, 0) + 1

        slot_duplicati = {s for s, count in conteggio_slot.items() if count > 1}
        mappa_colori_duplicati = {
            slot: PALETTE_DUPLICATI[i % len(PALETTE_DUPLICATI)]
            for i, slot in enumerate(slot_duplicati)
        }

        def _formatta_anteprima(item):
            tipo = item.get("tipo", "")
            dato = item.get("dato", "")
            if tipo == "File/Cartelle" and dato:
                percorsi = [p.strip() for p in dato.split(";") if p.strip()]
                from pathlib import Path
                if solo_nome_file:
                    return "; ".join([Path(p).name for p in percorsi])
                else:
                    return ";\n".join(percorsi)
            return item.get("anteprima", "")

        def _aggiungi_riga(row, slot_text, tipo_text, anteprima_text, note_text, colore=None, bloccato=False):
            self.table.insertRow(row)
            num_righe = anteprima_text.count("\n") + 1
            self.table.setRowHeight(row, min(max(34, num_righe * 18 + 10), 95))

            slot_vis = f"🔒 {slot_text.upper()}" if (bloccato and slot_text) else slot_text.upper()
            it_slot = QTableWidgetItem(slot_vis)
            it_slot.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_slot.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
            if colore: it_slot.setBackground(colore)
            self.table.setItem(row, 0, it_slot)

            it_tipo = QTableWidgetItem(tipo_text)
            it_tipo.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            if colore: it_tipo.setBackground(colore)
            self.table.setItem(row, 1, it_tipo)

            txt_box = QTextEdit()
            txt_box.setReadOnly(True)
            txt_box.setPlainText(anteprima_text)
            bg_hex = colore.name() if colore else "#f1f8e9"
            txt_box.setStyleSheet(f"""
                QTextEdit {{ background-color: {bg_hex}; color: #1b4332; border: none; font-size: 9pt; }}
                QScrollBar:vertical {{ border: none; background: transparent; width: 6px; margin: 0px; }}
                QScrollBar::handle:vertical {{ background: #a5d6a7; min-height: 12px; border-radius: 3px; }}
            """)
            self.table.setCellWidget(row, 2, txt_box)

            it_note = QTableWidgetItem(note_text)
            it_note.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
            if colore: it_note.setBackground(colore)
            self.table.setItem(row, 3, it_note)

        for row, item in enumerate(memoria):
            slot = item.get("slot", "").strip().lower()
            colore = mappa_colori_duplicati.get(slot, None)
            _aggiungi_riga(row, slot, item.get("tipo", ""), _formatta_anteprima(item), item.get("note", ""), colore, item.get("bloccato", False))

        for item in elementi_massivi:
            row = self.table.rowCount()
            _aggiungi_riga(row, "", item.get("tipo", ""), _formatta_anteprima(item), item.get("note", ""))

        self.table.blockSignals(False)
        if hasattr(self, 'keyboard_map'):
            self.keyboard_map.aggiorna_mappa(memoria)

