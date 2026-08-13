import json

from config import STREAM_NAME, CONSUMER_GROUP, CONSUMER_NAME
from redis_client import client
from services.sender import send_email
from services.templates import welcome_email, expense_split_email, monthly_summary_email

HANDLERS = {
    "welcome": welcome_email,
    "expense_split": expense_split_email,
    "monthly_summary": monthly_summary_email,
}


def recipients_for(event_type, payload):
    if event_type == "welcome":
        return [payload["email"]]
    return [member["email"] for member in payload["members"]]


def process(fields):
    event_type = fields["type"]
    payload = json.loads(fields["payload"])

    handler = HANDLERS.get(event_type)
    if not handler:
        print(f"unknown event type: {event_type}")
        return

    subject, body = handler(payload)

    for to in recipients_for(event_type, payload):
        try:
            send_email(to, subject, body)
            print(f"sent {event_type} to {to}")
        except Exception as e:
            print(f"FAILED sending {event_type} to {to}: {e}")


def run():
    print(f"worker '{CONSUMER_NAME}' listening on stream '{STREAM_NAME}'...")
    while True:
        resp = client.xreadgroup(
            CONSUMER_GROUP, CONSUMER_NAME, {STREAM_NAME: ">"}, block=5000, count=10
        )
        if not resp:
            continue

        for _stream_name, entries in resp:
            for entry_id, fields in entries:
                process(fields)
                client.xack(STREAM_NAME, CONSUMER_GROUP, entry_id)


if __name__ == "__main__":
    run()
