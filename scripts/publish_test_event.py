import json
import sys

from config import STREAM_NAME
from redis_client import client

EVENTS = {
    "welcome": {
        "type": "welcome",
        "payload": json.dumps({"email": "sankar.s@broccly.com", "name": "Sankar"}),
    },
    "expense_split": {
        "type": "expense_split",
        "payload": json.dumps({
            "expense_title": "Groceries",
            "total_pending": 500,
            "members": [
                {"name": "Sankar", "email": "sankar.s@broccly.com", "pending_amount": 250},
                {"name": "Ravi", "email": "ravi@s.com", "pending_amount": -250},
            ],
            "settlements": [
                {"from_name": "Ravi", "to_name": "Sankar", "amount": 250},
            ],
        }),
    },
    "monthly_summary": {
        "type": "monthly_summary",
        "payload": json.dumps({
            "month": "August 2026",
            "expenses": [
                {"title": "Groceries", "amount": 500, "paid_by": "Sankar", "participants": ["Sankar", "Ravi"], "date": "2026-08-03"},
                {"title": "Gas bill", "amount": 300, "paid_by": "Ravi", "participants": ["Sankar", "Ravi"], "date": "2026-08-10"},
                {"title": "Internet", "amount": 400, "paid_by": "Sankar", "participants": ["Sankar", "Ravi"], "date": "2026-08-15"},
            ],
            "members": [
                {"name": "Sankar", "email": "sankar.s@broccly.com", "total_paid": 900, "total_share": 600},
                {"name": "Ravi", "email": "ravi@s.com", "total_paid": 300, "total_share": 600},
            ],
        }),
    },
}

if __name__ == "__main__":
    event_name = sys.argv[1] if len(sys.argv) > 1 else "welcome"
    event = EVENTS[event_name]
    client.xadd(STREAM_NAME, event)
    print(f"published '{event_name}' event")
