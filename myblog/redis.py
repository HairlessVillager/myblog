from os import getenv

import redis

client = redis.from_url(getenv("REDIS_URL"), decode_responses=True)


def get_slug(id: int) -> str | None:
    return client.get(f"{id}-slug")


def get_html(id: int) -> str | None:
    return client.get(f"{id}-html")


def set_slug(id: int, slug: str):
    client.set(f"{id}-slug", slug, ex=60)


def set_html(id: int, html: str):
    client.set(f"{id}-html", html, ex=60)
