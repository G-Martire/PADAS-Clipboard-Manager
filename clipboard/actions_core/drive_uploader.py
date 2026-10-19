"""
PADAS CLIPBOARD MANAGER - DRIVE UPLOADER
Modulo helper per l'autenticazione ed il caricamento di immagini su Google Drive via API.
"""

import os
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = Path("credentials.json")
TOKEN_FILE = Path("token.json")


class GoogleDriveService:
    """Gestisce la connessione con le API di Google Drive e l'upload dei file."""

    @classmethod
    def ottieni_servizio(cls):
        """Autentica l'utente e restituisce l'istanza del servizio Google Drive."""
        creds = None

        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            except Exception as err:
                logging.warning(f"[DRIVE-API] Impossibile caricare token.json: {err}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as err:
                    logging.warning(f"[DRIVE-API] Impossibile aggiornare il token: {err}")
                    creds = None

            if not creds:
                if not CREDENTIALS_FILE.exists():
                    raise FileNotFoundError(
                        "File 'credentials.json' non trovato nella cartella principale di PADAS!\n"
                        "Scarica le credenziali OAuth 2.0 da Google Cloud Console e rinominale in 'credentials.json'."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())

        return build('drive', 'v3', credentials=creds)

    @classmethod
    def carica_immagine_e_ottieni_link(cls, file_path: Path, nome_remoto: str = None) -> str:
        """
        Carica un file immagine su Google Drive, imposta i permessi di lettura
        e restituisce il link web di condivisione.
        """
        service = cls.ottieni_servizio()

        filename = nome_remoto or file_path.name
        file_metadata = {
            'name': filename,
            'mimeTypes': 'image/png'
        }

        media = MediaFileUpload(str(file_path), mimetype='image/png', resumable=True)

        logging.info(f"[DRIVE-API] Inizio upload di '{filename}' su Google Drive...")
        drive_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        file_id = drive_file.get('id')
        web_link = drive_file.get('webViewLink')

        # Imposta i permessi per permettere la visualizzazione dell'anteprima tramite link
        permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()

        logging.info(f"[DRIVE-API] Upload completato con successo. Link: {web_link}")
        return web_link

