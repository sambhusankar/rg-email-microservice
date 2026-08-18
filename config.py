import os

from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

RESEND_API_KEY = os.environ["RESEND_API_KEY"]
FROM_EMAIL = os.environ["FROM_EMAIL"]
FROM_NAME = os.environ.get("FROM_NAME", "RoomGrub")

STREAM_NAME = "rg:emails"
CONSUMER_GROUP = "email-workers"
CONSUMER_NAME = os.environ.get("CONSUMER_NAME", "worker-1")
