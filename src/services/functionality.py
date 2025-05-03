import logging

from .imap import EmailFilter, EmailParserService, EmailDetailsExtractor, EmailTrashService
import socket
import csv
from typing import TextIO, Sequence, Any
from imapclient import IMAPClient
from collections import defaultdict


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
        writer = csv.DictWriter(file, fieldnames=["from", "subject", "date", "body"])  # noqa
        writer.writeheader()
        writer.writerows(data)


def move_to_trash(conn: IMAPClient, ids: Sequence[bytes])-> tuple[bool, str]:
    conn = conn
    email_ids = ids
    trash_service = EmailTrashService(conn)
    return trash_service.move_to_trash(email_ids)


def get_folders(conn: IMAPClient) -> list[tuple[str, str]]:
    folders = conn.list_folders()
    folder_names = []
    for flags, delimiter, name in folders:
        if isinstance(name, bytes):
            name = name.decode()
        if isinstance(delimiter, bytes):
            delimiter = delimiter.decode()

        # Skip Gmail system folders
        if name == '[Gmail]':
            continue
        # Handle Gmail-style names like "[Gmail]/Spam"
        if delimiter in name:
            clean_name = (name, name.split(delimiter)[-1])
        else:
            clean_name = (name, name)
        folder_names.append(clean_name)
    return folder_names


def sorted_emails(emails: list[dict] ) -> list[tuple[str, dict[str, Any]]]:
    # Each sender maps to a list of their email UIDs
    sender_data = defaultdict(lambda: {"count": 0, "uids": []})

    for email in emails:
        sender = email["from"]
        uid = email["uid"]
        sender_data[sender]["count"] += 1
        sender_data[sender]["uids"].append(uid)

    # Sort by count
    sorted_senders = sorted(sender_data.items(), key=lambda x: x[1]["count"], reverse=True)

    return sorted_senders

class EmailSearchError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


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


    def get_email_ids(self, chosen_folder: str):
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
        parser = EmailParserService(server=self.conn, folder=chosen_folder)
        # Search for email IDs using the filter criteria
        self.ids = parser.search_emails(self.filters)
        # Check if the search returned a list of email IDs (successful search).
        if not isinstance(self.ids, list):
            raise EmailSearchError(f"Search failed: {self.ids}")

        return self.ids

    def get_email_data(self, key: str) -> list[dict[str, str]] | str:
        """ Retrieves email details based on the Ids provided.
                It performs the following steps:
                  1. Creates an EmailDetailsExtractor with the ids provided.
                  2. Fetch the data from emails found by ids
                :return: A list of dictionaries (each containing email 'from', 'date', and 'body') if successful,
                         otherwise an error message string."""

        # Instantiate the extractor service to fetch the complete details for the email IDs.
        extractor = EmailDetailsExtractor(self.conn, self.ids)
        email_details: dict = {
            "ALL": extractor.fetch_all_email_details,
            "CURTAIN" : extractor.fetch_curtain_email_details
        }

        return email_details[key]()
