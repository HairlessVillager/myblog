from logging import getLogger
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from .model import (
    Blog,
    engine,
)

logger = getLogger("app")


def get_blog(id: int) -> Blog | None:
    with Session(engine) as session:
        blog = session.get(Blog, id)
        if not blog:
            logger.warning(
                f"get_blog({id=}): blog not found"
            )  # TODO: remove this warning
        return blog


def get_blogs_sorted_by_id() -> Sequence[Blog]:
    with Session(engine) as session:
        stmt = select(Blog).order_by(Blog.id)
        blogs = session.scalars(stmt).all()
        return blogs


def get_pinned_blogs_sorted_by_id() -> Sequence[Blog]:
    with Session(engine) as session:
        stmt = select(Blog).where(Blog.pinned == True).order_by(Blog.id)
        blogs = session.scalars(stmt).all()
        return blogs


def update_blog(blog: Blog):
    with Session(engine) as session:
        session.merge(blog)
        session.commit()


def create_blog(blog: Blog) -> int:
    with Session(engine) as session:
        session.add(blog)
        session.commit()
        return blog.id
