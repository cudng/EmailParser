import logging
import re
from dataclasses import dataclass
from typing import Optional, Sequence
from email import message_from_bytes
from email.header import decode_header
from bs4 import BeautifulSoup
from imapclient import IMAPClient, exceptions as imap_exceptions
import ssl


class EmailConnectionService:
    def __init__(self, email: str, password: str, imap_server: str, port: int = 993):
        self.imap_server = imap_server
        self.port = port
        self.email = email
        self.password = password

    def connect(self):
        try:
            context = ssl.create_default_context()
            connection = IMAPClient(
                host=self.imap_server,
                port=self.port,
                ssl=True,
                ssl_context=context,
                use_uid=True  # recommended: always work with UIDs
            )
            connection.login(self.email, self.password)
            return connection  # Return live IMAPClient connection
        except imap_exceptions.LoginError as e:
            logging.warning(e)
            return f"IMAP login error: {str(e)}"
        except Exception as e:
            logging.warning(e)
            return f"Connection error: {str(e)}"



def decode_mime_words(s):
    decoded_parts = decode_header(s)
    decoded_string = ''
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                decoded_string += part.decode(charset or 'utf-8', errors='replace')
            except (LookupError, TypeError):
                # Fallback if charset is unknown or invalid
                decoded_string += part.decode('utf-8', errors='replace')
        else:
            decoded_string += part
    return decoded_string


@dataclass
class EmailFilter:
    sender: Optional[str] = None
    subject: Optional[str] = None
    since: Optional[str] = None  # Format: DD-MM-YYYY
    before: Optional[str] = None  # Format: DD-MM-YYYY
    text: Optional[str] = None  # Full-text search in body/subject

    def to_imap_query(self) -> list:
        query = []

        for key, value in self.__dict__.items():
            if value is None:
                continue

            match key:
                case "sender":
                    query += ['FROM', f'"{value}"']
                case "subject":
                    query += ['SUBJECT', f'"{value}"']
                case "since":
                    query += ['SINCE', f'"{value}"']
                case "before":
                    query += ['BEFORE', f'"{value}"']
                case "text":
                    query += ['TEXT', f'"{value}"']

        return query if query else ["ALL"]


class EmailParserService:
    def __init__(self, server: IMAPClient, folder: str):
        self.server = server
        self.server.select_folder(folder)

    def search_emails(self, filters: EmailFilter) -> list[bytes]:
        """
        Returns list of UIDs matching the criteria.
        """
        # filters.to_imap_query might return like ['FROM', 'alice@example.com']
        criteria = filters.to_imap_query()
        uids = self.server.search(criteria)  # returns UIDs by default :contentReference[oaicite:3]{index=3} # noqa
        return uids


class EmailDetailsExtractor:
    def __init__(self, server: IMAPClient, uids: list[int]):
        self.server = server
        self.uids = uids

    def fetch_all_email_details(self) -> list[dict]: # noqa
        if not self.uids:
            return []

        # 1) Batch‑fetch full RFC822 payloads
        messages = self.server.fetch(self.uids, ['RFC822'])  # :contentReference[oaicite:3]{index=3} # noqa
        if not messages:
            return [{"error": "Server returned no messages"}]

        details = []
        for uid, data in messages.items():
            if b'RFC822' not in data:
                continue  # skip any malformed entries

            raw = data[b'RFC822']
            msg = message_from_bytes(raw)                # :contentReference[oaicite:4]{index=4} # noqa

            subject = decode_mime_words(msg.get('Subject', ''))
            sender  = decode_mime_words(msg.get('From', '')).strip('<>')
            date    = msg.get('Date', '').split('+')[0]
            body    = self._get_body(msg)

            details.append({
                'subject': subject,
                'from':    sender,
                'date':    date,
                'body':    ' '.join(body.split()),
                'uid': uid
            })

        return details

    def fetch_curtain_email_details(self) -> list[dict]:
        if not self.uids:
            return []

        messages = self.server.fetch(self.uids, ['BODY.PEEK[HEADER.FIELDS (FROM)]'])
        if not messages:
            return [{"error": "Server returned no messages"}]

        details = []
        for uid, data in messages.items():
            header_data = data.get(b'BODY[HEADER.FIELDS (FROM)]')
            if not header_data:
                continue

            msg = message_from_bytes(header_data)
            sender = decode_mime_words(msg.get('From', '')).strip('<>')

            details.append({
                'from': sender,
                'uid': uid
            })

        return details

    @staticmethod
    def _get_body(msg) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition") or "")
                if content_type == "text/plain" and "attachment" not in content_disposition.lower():
                    body_bytes = part.get_payload(decode=True)
                    if body_bytes:
                        return body_bytes.decode(errors="ignore")

            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_bytes = part.get_payload(decode=True)
                    if html_bytes:
                        html = html_bytes.decode(errors="ignore")
                        soup = BeautifulSoup(html, "html.parser")
                        text = soup.get_text(separator="\n") # noqa
                        return re.sub(r'(?i)<!doctype html[^>]*>', '', text).strip()
        else:
            body_bytes = msg.get_payload(decode=True)
            if body_bytes:
                text = body_bytes.decode(errors="ignore")
                soup = BeautifulSoup(text, "html.parser")
                text = soup.get_text(separator="\n") # noqa
                return re.sub(r'(?i)<!doctype html[^>]*>', '', text).strip()

        return ""


class EmailTrashService:
    def __init__(self, server: IMAPClient, trash_folder: str = '[Gmail]/Bin'):
        self.server = server
        self.trash = trash_folder

    def move_to_trash(self, uids: Sequence[bytes]) -> tuple[bool, str]: # noqa
        if not uids:
            return False, 'No emails to move.'

        self.server.copy(uids, self.trash)
        self.server.set_flags(uids, ['\\Deleted'], silent=True)
        self.server.expunge()
        return True, f'Moved {len(uids)} message(s) to {self.trash}.'


