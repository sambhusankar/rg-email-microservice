import json
import sys

from config import STREAM_NAME
from redis_client import client

EVENTS = {
    "welcome": {
        "type": "welcome",
        "payload": json.dumps({"email": "sankar@s.com", "name": "Sankar"}),
    },
    "expense_split": {
        "type": "expense_split",
        "payload": json.dumps({
            "expense_title": "Groceries",
            "paid_by": "Sankar",
            "members": [
                {"name": "Sankar", "email": "sankar@s.com", "amount_owed": 250},
                {"name": "Ravi", "email": "ravi@s.com", "amount_owed": 250},
            ],
        }),
    },
    "monthly_summary": {
        "type": "monthly_summary",
        "payload": json.dumps({
            "month": "August 2026",
            "members": [
                {"name": "Sankar", "email": "sankar@s.com", "total_owed": 1200},
                {"name": "Ravi", "email": "ravi@s.com", "total_owed": 800},
            ],
        }),
    },
}

if __name__ == "__main__":
    event_name = sys.argv[1] if len(sys.argv) > 1 else "welcome"
    event = EVENTS[event_name]
    client.xadd(STREAM_NAME, event)
    print(f"published '{event_name}' event")
