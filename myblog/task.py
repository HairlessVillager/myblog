from datetime import datetime
import logging

from jinja2 import Template
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .query import (
    get_blog,
    get_blogs_sorted_by_id,
    update_blog,
)
from .model import (
    UpdateBlogForm,
)
from .schedule import (
    SchedulerMiddleware,
)

logger = logging.getLogger("app")


@SchedulerMiddleware.register(IntervalTrigger(seconds=10), paused=True)
async def update_home():
    from .query import update_blog

    blog = await get_blog(1)
    if blog:
        text = blog.text
        text += f"- {datetime.now()}\n"
        form = UpdateBlogForm(text=text, token="")
        form.update(blog)
        await update_blog(blog)
        logger.info("update_home: successfully")
    else:
        logger.error("update_home: home not exists")


async def update_blog_content():
    template = Template(
        """{% for blog in blogs %}
- {{ blog.create_at }} [{{ blog.title }}](/blog/{{ blog.id }}/{{ blog.slug }})
{% endfor %}
"""
    )
    text = template.render(blogs=await get_blogs_sorted_by_id())
    blog = await get_blog(2)
    if blog:
        blog.text = text
        await update_blog(blog)
        logger.info("update_blog_content: successfully")
    else:
        logger.error("update_blog_content: blog(id=2) not exists")
