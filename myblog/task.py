from datetime import timedelta, timezone
import logging

from jinja2 import Template

from .query import (
    get_blog,
    get_blogs_sorted_by_id,
    update_blog,
)

logger = logging.getLogger("app")


async def update_blog_content():
    template = Template(
        """{% for blog in blogs %}
- {{ blog.create_at }} [{{ blog.title }}](/blog/{{ blog.id }}/{{ blog.slug }})
{% endfor %}
"""
    )
    blogs = await get_blogs_sorted_by_id()
    logger.debug(f"update_home: {blogs=}")
    for blog in blogs:
        blog.create_at = blog.create_at.astimezone(tz=timezone(timedelta(hours=8)))
        blog.update_at = blog.update_at.astimezone(tz=timezone(timedelta(hours=8)))
    text = template.render(blogs=blogs)
    blog = await get_blog(2)
    if blog:
        blog.text = text
        await update_blog(blog)
        logger.info("update_blog_content: successfully")
    else:
        logger.error("update_blog_content: blog(id=2) not exists")
