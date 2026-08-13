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
  sender.py                # send_email(to, subject, html) via Resend
  templates.py              # subject/body builders per event type
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
```json
{
  "expense_title": "Groceries",
  "paid_by": "Sankar",
  "members": [
    { "name": "Sankar", "email": "sankar@example.com", "amount_owed": 250 },
    { "name": "Ravi", "email": "ravi@example.com", "amount_owed": 250 }
  ]
}
```

### `monthly_summary`
```json
{
  "month": "August 2026",
  "members": [
    { "name": "Sankar", "email": "sankar@example.com", "total_owed": 1200 },
    { "name": "Ravi", "email": "ravi@example.com", "total_owed": 800 }
  ]
}
```

## Why consumer groups

Plain Redis Pub/Sub drops messages if the worker isn't running when they're
published. Using `XREADGROUP`/`XACK` on a stream means unacknowledged
messages stay pending in Redis and can be reclaimed after a crash or
restart, instead of a user silently never getting their expense email.
