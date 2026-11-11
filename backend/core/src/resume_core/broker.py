"""Explicit local Redis adapter; constructing it never starts a Redis server."""

import re
from urllib.parse import urlsplit

from dramatiq import Message
from dramatiq.brokers.redis import RedisBroker
from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry

QUEUE = "diagnostics"
ACTOR = "run_diagnostic"


def make_broker(url: str, namespace: str = "resume-builder-development") -> RedisBroker:
    parsed = urlsplit(url)
    if parsed.scheme != "redis" or parsed.hostname != "127.0.0.1":
        raise ValueError("Redis requires an explicit loopback URL")
    if not re.fullmatch(r"[a-zA-Z0-9_:-]{1,128}", namespace):
        raise ValueError("Invalid Redis namespace")
    client = Redis.from_url(
        url,
        socket_connect_timeout=0.2,
        socket_timeout=0.2,
        retry=Retry(NoBackoff(), 0),
        retry_on_timeout=False,
    )
    return RedisBroker(client=client, namespace=namespace)


class RedisPublisher:
    def __init__(self, broker):
        self.broker = broker

    def publish(self, delivery):
        self.broker.declare_queue(QUEUE)
        self.broker.enqueue(
            Message(
                queue_name=QUEUE,
                actor_name=ACTOR,
                args=(str(delivery.id), str(delivery.request_id)),
                kwargs={},
                options={"max_retries": 0},
            )
        )
