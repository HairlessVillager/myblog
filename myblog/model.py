from typing import Optional, Any
from datetime import datetime
from os import getenv
from dataclasses import dataclass

from pydantic import BaseModel as PydaticBase
from motor.motor_asyncio import AsyncIOMotorClient

from .auth import (
    get_now,
)


@dataclass
class Blog:
    id: int | None
    title: str
    pinned: bool
    deleted: bool
    slug: str
    create_at: datetime
    update_at: datetime
    text: str
    html: Optional[str]

    def into_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "pinned": self.pinned,
            "deleted": self.deleted,
            "slug": self.slug,
            "create_at": self.create_at,
            "update_at": self.update_at,
            "text": self.text,
            "html": self.html,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Blog":
        return cls(
            id=d["id"],
            title=d["title"],
            pinned=d["pinned"],
            deleted=d["deleted"],
            slug=d["slug"],
            create_at=d["create_at"],
            update_at=d["update_at"],
            text=d["text"],
            html=d["html"],
        )


class CreateBlogForm(PydaticBase):
    title: str
    pinned: bool
    deleted: bool
    slug: str
    text: str
    token: str

    def to_blog(self) -> Blog:
        return Blog(
            id=None,
            html=None,
            title=self.title,
            pinned=self.pinned,
            deleted=self.deleted,
            slug=self.slug,
            text=self.text,
            create_at=get_now("NOTZ"),
            update_at=get_now("NOTZ"),
        )


class UpdateBlogForm(PydaticBase):
    title: str | None = None
    pinned: bool | None = None
    deleted: bool | None = None
    slug: str | None = None
    text: str | None = None
    token: str

    def update(self, blog: Blog) -> Blog:
        blog.update_at = get_now("NOTZ")
        if self.title:
            blog.title = self.title
        if self.pinned:
            blog.pinned = self.pinned
        if self.deleted:
            blog.deleted = self.deleted
        if self.slug:
            blog.slug = self.slug
        if self.text:
            blog.text = self.text
        return blog


client = AsyncIOMotorClient(getenv("DB_URL"))
