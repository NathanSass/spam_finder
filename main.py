import os
import asyncio

from agents.link_verifying_agent import LinkVerifyingAgent
from agents.query_parse_agent import QueryParsingAgent
from utils.html_parser import get_email_data
from integrations.gmail_provider import GmailProvider


# We will pass a query string parameter here with what we want to parse
#   uvicorn main:app --reload
#   GET http://127.0.0.1:8000/query?message="You have an important message waiting in your Chase Secure Message Center. <https://ad.doubleclick.verysafelink.com/afj40923|Click here!>.
async def handle_query(query: str):
    """
    Steps:
    1. Parse the input (text message, email, etc.)
    2. Verify the links within the input
    3. Determine whether it contains spam or not
    """
    parsed_query = QueryParsingAgent().parse_query(query)
    link_info = LinkVerifyingAgent().verify_links(parsed_query)
    return link_info


async def process_messages(gmail_provider):
    while True:
        messages = gmail_provider.get_messages()
        if not messages:
            print("No new messages.")
        else:
            print(f"Processing {len(messages)} new message(s)")
            for message in messages:
                message_id = message["id"]
                msg = gmail_provider.get_message_details(message_id)
                email_details_cleaned = get_email_data(msg)
                result = await handle_query(email_details_cleaned)
                print(result)
                if result["is_spam"]:
                    print("Labelling as spam")
                    gmail_provider.modify_label(
                        message_id, os.getenv("GMAIL_SPAM_LABEL_ID")
                    )  # this label corresponds to the "Spam Detected" label
                gmail_provider.mark_as_read(message_id)
        await asyncio.sleep(15)  # Poll every 15 seconds


def main():
    gmail_provider = GmailProvider()
    asyncio.run(process_messages(gmail_provider))


if __name__ == "__main__":
    main()
