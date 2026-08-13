import redis

from config import STREAM_NAME, CONSUMER_GROUP
from redis_client import client


def ensure_group():
    try:
        client.xgroup_create(STREAM_NAME, CONSUMER_GROUP, id="0", mkstream=True)
        print(f"created group {CONSUMER_GROUP} on {STREAM_NAME}")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
        print(f"group {CONSUMER_GROUP} already exists on {STREAM_NAME}")


if __name__ == "__main__":
    ensure_group()
