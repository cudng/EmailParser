from .imap import EmailFilter, EmailParserService, EmailDetailsExtractor, EmailTrashService
import socket
import csv
from typing import TextIO, Sequence
from imapclient import IMAPClient


def is_connected(host="8.8.8.8", port=53, timeout=2):
    """
    Attempts to connect to a DNS server (Google's 8.8.8.8) to check internet access.
    Returns True if connected, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception: # noqa
        return False


def save_emails_to_csv(file_path: str, data: list[dict[str, str]]):
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:  # type: TextIO
        writer = csv.DictWriter(file, fieldnames=["from", "subject", "date", "body"])
        writer.writeheader()
        writer.writerows(data)


class EmailSearchError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DeleteEmails:

    def __init__(self, conn: IMAPClient, ids: Sequence[bytes]) -> None:
        self.conn = conn
        self.email_ids = ids
        self.trash_service = EmailTrashService(self.conn)

    def move_to_trash(self) -> tuple[bool, str]:

         return self.trash_service.move_to_trash(self.email_ids)


class SearchEmails:
    """
        A class to perform email searches using IMAP-based services.

        This class:
          - Accepts filter criteria as a dictionary and an existing IMAP connection.
          - Initializes an EmailFilter based on provided filter values.
          - Uses EmailParserService to get email IDs based on filter criteria.
          - Uses EmailDetailsExtractor to fetch and return details for the found email IDs.

        Returns:
          A list of dictionaries with email details if successful, or an error string otherwise.
        """
    def __init__(self, filters: dict[str, str], conn: IMAPClient):
        """
                Initializes the SearchEmails class.

                :param filters: A dictionary containing filter criteria (e.g., sender, subject).
                :param conn: An active connection object (typically an imaplib.IMAP4_SSL connection).
                """
        # Instantiate an EmailFilter using the dictionary's keys as arguments.
        self.filters = EmailFilter(**filters)
        self.conn = conn
        self.ids = None


    def get_email_ids(self):
        """
                        Retrieves email details based on the filters and the provided connection.

                        It performs the following steps:
                          1. Creates an EmailParserService with the current connection.
                          2. Searches for emails using the filter.
                          3. If email IDs are returned (as a list), returns a list
                          4. If the search returns an error (i.e., not a list), an error string is returned.

                        :return: A list of email ids if successful,
                                 otherwise an error message string.
                        """
        # Instantiate the parser service using the active connection.
        parser = EmailParserService(server=self.conn)
        # Search for email IDs using the filter criteria
        self.ids = parser.search_emails(self.filters)
        # Check if the search returned a list of email IDs (successful search).
        if not isinstance(self.ids, list):
            raise EmailSearchError(f"Search failed: {self.ids}")

        return self.ids

    def get_email_data(self) -> list[dict[str, str]] | str:
        """
                Retrieves email details based on the Ids provided.

                It performs the following steps:
                  1. Creates an EmailDetailsExtractor with the ids provided.
                  2. Fetch the data from emails found by ids

                :return: A list of dictionaries (each containing email 'from', 'date', and 'body') if successful,
                         otherwise an error message string.
                """

        # Instantiate the extractor service to fetch the complete details for the email IDs.
        extractor = EmailDetailsExtractor(self.conn)
        email_details = extractor.fetch_all_email_details(self.ids)

        return email_details
