import html.parser
import email
import base64


class HTMLTextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super(HTMLTextExtractor, self).__init__()
        self.result = []

    def handle_data(self, d):
        self.result.append(d)

    def get_text(self):
        return "".join(self.result)


def html_to_text(html):
    s = HTMLTextExtractor()
    s.feed(html)
    return s.get_text()


def get_email_data(email_msg):
    body = None
    html = ""

    email_subject = email_msg.get_all("Subject")
    from_sender = email_msg.get_all("From")
    to_recipient = email_msg.get_all("To")
    return_path = email_msg.get_all("Return-Path")
    delivered_to = email_msg.get_all("Delivered-To")
    datetime_rx = email_msg.get_all("Date")

    if email_msg.is_multipart():
        for part in email_msg.walk():
            content_type = part.get_content_type()
            disp = str(part.get("Content-Disposition"))
            # look for plain text parts, but skip attachments
            if part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                body = part.get_payload(decode=True)
                continue
            if content_type == "text/plain" and "attachment" not in disp:
                charset = part.get_content_charset()
                # decode the base64 unicode bytestring into plain text
                body = part.get_payload(decode=True).decode(
                    encoding=charset, errors="ignore"
                )
                # if we've found the plain/text part, stop looping thru the parts
                break
            if content_type == "text/html" and "attachment" not in disp:
                charset = part.get_content_charset()
                html = part.get_payload(decode=True).decode(
                    encoding=charset, errors="ignore"
                )
                # if we've found the plain/text part, stop looping thru the parts
                break
    else:
        # not multipart - i.e. plain text, no attachments
        content_type = email_msg.get_content_type()
        if email_msg.get_content_charset() is None:
            # We cannot know the character set, so return decoded "something"
            body = email_msg.get_payload(decode=True)
        else:
            charset = email_msg.get_content_charset()
            if content_type == "text/plain":
                body = email_msg.get_payload(decode=True).decode(
                    encoding=charset, errors="ignore"
                )
            if content_type == "text/html":
                html = email_msg.get_payload(decode=True).decode(
                    encoding=charset, errors="ignore"
                )
    if body is not None:
        body = body.strip()
    else:
        body = html_to_text(html)
        body = body.strip()
    return {
        "body": body,
        "delivered_to": delivered_to,
        "return_path": return_path,
        "from_sender": from_sender,
        "to_recipient": to_recipient,
        "datetime_rx": datetime_rx,
        "email_subject": email_subject,
    }
