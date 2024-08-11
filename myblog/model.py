from datetime import datetime
from os import getenv

from pydantic import BaseModel as PydaticBase
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from .auth import (
    get_now,
)


class SqlalchemyBase(DeclarativeBase):
    pass


class Blog(SqlalchemyBase):
    __tablename__ = "blogs"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    pinned: Mapped[bool]
    deleted: Mapped[bool]
    slug: Mapped[str]
    create_at: Mapped[datetime]  # TODO: use sqla
    update_at: Mapped[datetime]  # TODO: use sqla
    text: Mapped[str]

    def __repr__(self):
        return f"{self.id} {self.title}"


class CreateBlogForm(PydaticBase):
    title: str
    pinned: bool
    deleted: bool
    slug: str
    text: str
    token: str

    def to_blog(self) -> Blog:
        return Blog(
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


engine = create_engine(
    getenv("DB_URL_SYNC"),
    echo=False,
)
