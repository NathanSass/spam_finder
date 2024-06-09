import os.path
import base64
import pickle
import email

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailProvider:
    def __init__(self):
        self._service = self.authenticate_gmail()

    def authenticate_gmail(self):
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8080)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        service = build("gmail", "v1", credentials=creds)
        return service

    def get_messages(self, query="is:unread"):
        results = self._service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        return messages

    def get_message_details(self, message_id):
        message = (
            self._service.users()
            .messages()
            .get(userId="me", id=message_id, format="raw")
            .execute()
        )
        msg_str = base64.urlsafe_b64decode(message["raw"].encode("ASCII"))
        email_msg = email.message_from_bytes(msg_str)
        return email_msg

    def modify_label(self, message_id, label):
        message = (
            self._service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"addLabelIds": [label]})
            .execute()
        )
        print("Label updated on message.")

    def mark_as_read(self, message_id):
        """
        Marks an email as read by removing the 'UNREAD' label.

        :param message_id: The ID of the email message to mark as read.
        """
        try:
            self._service.users().messages().modify(
                userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            print(f"Message with ID {message_id} marked as read.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_labels(self, message_id):
        labels = (
            self._service.users()
            .messages()
            .get(userId="me", id=message_id, format="metadata")
            .execute()
            .get("labelIds")
        )
