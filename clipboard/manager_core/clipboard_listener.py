"""
PADAS CLIPBOARD MANAGER - CLIPBOARD LISTENER MIXIN
Gestisce il monitoraggio nativo della Clipboard di Sistema tramite Qt e il filtraggio anti-duplicati con hash MD5.
"""

import time
import logging
import hashlib
import winsound
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QBuffer, QIODevice


class ClipboardListenerMixin:
    """Mixin per la gestione degli eventi di modifica della clipboard di sistema[cite: 6]."""

    def _connetti_listener_clipboard(self):
        """Collega il listener nativo Qt per qualsiasi modifica alla Clipboard di Sistema[cite: 6]."""
        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self._on_clipboard_data_changed)

    def _on_clipboard_data_changed(self):
        """Reagisce istantaneamente a QUALSIASI nuovo dato in clipboard con filtro hash sicuro[cite: 6]."""
        if self.cattura_massiva_attiva and not self._blocco_cattura_massiva:
            self._blocco_cattura_massiva = True
            try:
                clipboard = QApplication.clipboard()
                mime = clipboard.mimeData()
                
                impronta_corrente = None

                if mime.hasImage():
                    img = clipboard.image()
                    if not img.isNull():
                        buffer = QBuffer()
                        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                        img.save(buffer, "PNG")
                        raw_bytes = buffer.data().data()
                        buffer.close()
                        impronta_corrente = f"IMG_{img.width()}x{img.height()}_{hashlib.md5(raw_bytes).hexdigest()}"
                elif mime.hasText():
                    txt_bytes = mime.text().strip().encode('utf-8')
                    impronta_corrente = f"TXT_{hashlib.md5(txt_bytes).hexdigest()}"
                elif mime.hasUrls():
                    urls_str = "".join([u.toString() for u in mime.urls()]).encode('utf-8')
                    impronta_corrente = f"URL_{hashlib.md5(urls_str).hexdigest()}"

                ora_attuale = time.time()
                impronta_ultima = getattr(self, "_ultima_impronta_salvata", None)
                tempo_ultimo = getattr(self, "_ultimo_timestamp_salvataggio", 0)

                if impronta_corrente and impronta_corrente == impronta_ultima:
                    if (ora_attuale - tempo_ultimo) < 2.0:
                        logging.info("[LOG-MANAGER] Evento duplicato (stessi byte entro 2s) ignorato[cite: 6].")
                        return

                logging.info("[LOG-MANAGER] Nuova risorsa valida rilevata in Clipboard -> Salvataggio in Cattura Massiva[cite: 6]...")
                self._estrai_e_salva_massivo()
                if impronta_corrente:
                    self._ultima_impronta_salvata = impronta_corrente
                    self._ultimo_timestamp_salvataggio = ora_attuale
                
                self._notifica_salvataggio()

            finally:
                time.sleep(0.08)
                self._blocco_cattura_massiva = False

    def _notifica_salvataggio(self):
        """Esegue la notifica acustica o visiva al salvataggio[cite: 6]."""
        tipo = self.config_notifiche.get("tipo", "bip")
        if tipo == "bip":
            try:
                winsound.Beep(1000, 120)
            except Exception:
                QApplication.beep()
        elif tipo == "popup":
            QMessageBox.information(self, "PADAS Clipboard", "Dato salvato in memoria!")

    def svuota_clipboard_sistema(self):
        """Azzera la clipboard di Windows sul Thread Principale di PyQt6[cite: 6]."""
        QApplication.processEvents()
        QApplication.clipboard().clear()
        try:
            winsound.Beep(600, 100)
        except Exception:
            pass

