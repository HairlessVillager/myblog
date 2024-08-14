from logging import getLogger
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from .model import (
    Blog,
    engine,
)

logger = getLogger("app")


async def get_blog(id: int) -> Blog | None:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        blog = await session.get(Blog, id)
        if not blog:
            logger.warning(
                f"get_blog({id=}): blog not found"
            )  # TODO: remove this warning
        return blog


async def get_blogs_sorted_by_id() -> Sequence[Blog]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(Blog).order_by(Blog.id)
        blogs = (await session.scalars(stmt)).all()
        return blogs


async def get_pinned_blogs_sorted_by_id() -> Sequence[Blog]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        stmt = select(Blog).where(Blog.pinned == True).order_by(Blog.id)
        blogs = (await session.scalars(stmt)).all()
        return blogs


async def update_blog(blog: Blog):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        blog.create_at = blog.create_at.replace(tzinfo=None)
        blog.update_at = blog.update_at.replace(tzinfo=None)
        await session.merge(blog)
        await session.commit()


async def create_blog(blog: Blog) -> int:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        session.add(blog)
        await session.commit()
        return blog.id
