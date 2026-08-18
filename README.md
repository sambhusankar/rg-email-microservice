# rg-email-microservice

Consumes room/expense events from a Redis Stream and sends the corresponding
transactional email (welcome, expense split, monthly summary) via Resend.

RoomGrub-backend owns all scheduling and split-calculation logic. This
service only reads events off the queue and sends mail.

## Project structure

```
main.py                 # entrypoint: ensures the consumer group exists, starts the worker
config.py                # all env vars, single load_dotenv() call
redis_client.py           # shared Redis connection
services/
  sender.py                # send_email(to, subject, html, attachments) via Resend
  templates.py              # subject/body/attachments builders per event type
  pdf_statement.py           # builds the monthly statement PDF (reportlab)
workers/
  setup_group.py             # one-off: creates the "email-workers" consumer group
  worker.py                 # xreadgroup loop: dispatch -> send -> xack
scripts/
  publish_test_event.py       # dev-only: publish a fake event to the stream
```

## Setup

1. Start Redis (Docker):
   ```
   docker run -d --name rg-redis -p 6379:6379 redis
   ```
2. Create a venv and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in `RESEND_API_KEY` and `FROM_EMAIL`.

## Running

```
python main.py
```

This creates the `email-workers` consumer group on stream `rg:emails` (if it
doesn't exist yet) and starts consuming.

## Trying it out

In another terminal, with the venv active, publish a test event:

```
python -m scripts.publish_test_event welcome
python -m scripts.publish_test_event expense_split
python -m scripts.publish_test_event monthly_summary
```

The running worker should print `sent <type> to <email>` and the message
should land in the recipient's inbox.

## Event contract

All events are published to a single stream, `rg:emails`, as a hash with
`type` and a JSON-encoded `payload` field.

### `welcome`
```json
{ "email": "user@example.com", "name": "Sankar" }
```

### `expense_split`
Sent after a room's balances are recomputed (e.g. once a new expense is
added). Mirrors the app's Splits screen: total pending, per-member
balances, and the simplified "who pays whom" settlement list.
```json
{
  "expense_title": "Groceries",
  "total_pending": 500,
  "members": [
    { "name": "Sankar", "email": "sankar@example.com", "pending_amount": 250 },
    { "name": "Ravi", "email": "ravi@example.com", "pending_amount": -250 }
  ],
  "settlements": [
    { "from_name": "Ravi", "to_name": "Sankar", "amount": 250 }
  ]
}
```
`pending_amount` follows the app's convention: positive = "gets back",
negative = "owes", ~0 = "settled up". `settlements` is the backend's
debt-simplified transaction list; omit or send an empty list when the
room is fully settled.

### `monthly_summary`
Sent once per month per room. The email body has a condensed summary;
a full itemized statement (every expense, who paid, who participated,
totals by member, top-spender analytics) is generated as a PDF and
attached, like a bank statement.
```json
{
  "month": "August 2026",
  "expenses": [
    { "title": "Groceries", "amount": 500, "paid_by": "Sankar", "participants": ["Sankar", "Ravi"], "date": "2026-08-03" },
    { "title": "Gas bill", "amount": 300, "paid_by": "Ravi", "participants": ["Sankar", "Ravi"], "date": "2026-08-10" }
  ],
  "members": [
    { "name": "Sankar", "email": "sankar@example.com", "total_paid": 500, "total_share": 400 },
    { "name": "Ravi", "email": "ravi@example.com", "total_paid": 300, "total_share": 400 }
  ]
}
```
`total_paid` is what the member actually paid across the month's
expenses; `total_share` is their portion of the total. `total_paid -
total_share` is their net position (positive = gets back, negative =
owes), shown in both the email body and the PDF. `date` is
`YYYY-MM-DD`; the PDF's "Expense History" table is sorted by it.

## Why consumer groups

Plain Redis Pub/Sub drops messages if the worker isn't running when they're
published. Using `XREADGROUP`/`XACK` on a stream means unacknowledged
messages stay pending in Redis and can be reclaimed after a crash or
restart, instead of a user silently never getting their expense email.
