from logging import getLogger
from typing import Sequence

from .model import (
    Blog,
    client,
)
from .util import (
    blog2md,
    md2html,
)

logger = getLogger("app")

blog_collection = client["myblog"]["blog"]


async def get_blog(id: int) -> Blog | None:
    blog = await blog_collection.find_one({"id": id})
    if not blog:
        logger.warning(f"get_blog({id=}): blog not found")  # TODO: remove this warning
        return None
    return Blog.from_dict(blog)


async def get_blogs_sorted_by_id() -> Sequence[Blog]:
    cursor = blog_collection.find().sort("id")
    blogs = await cursor.to_list(length=None)
    return [Blog.from_dict(b) for b in blogs]


async def get_pinned_blogs_sorted_by_id() -> Sequence[Blog]:
    cursor = blog_collection.find({"pinned": True}).sort("id")
    blogs = await cursor.to_list(length=None)
    return [Blog.from_dict(b) for b in blogs]


async def update_blog(blog: Blog):
    logger.debug(f"update_blog: {blog=}")
    blog.create_at = blog.create_at.replace(tzinfo=None)
    blog.update_at = blog.update_at.replace(tzinfo=None)
    blog.html = md2html(await blog2md(blog))
    await blog_collection.update_one({"id": blog.id}, {"$set": blog.into_dict()})
    new_blog = await blog_collection.find_one({"id": blog.id})
    logger.debug(f"update_blog: {new_blog=}")


async def create_blog(blog: Blog) -> int:
    total = await blog_collection.count_documents({})
    blog.id = total + 1
    await blog_collection.insert_one(blog.into_dict())
    return blog.id
