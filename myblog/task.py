from datetime import timedelta, timezone
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
from .auth import (
    get_now,
)

logger = logging.getLogger("app")


@SchedulerMiddleware.register(IntervalTrigger(seconds=10), paused=True)
def update_home():
    from .query import update_blog

    blog = get_blog(1)
    if blog:
        text = blog.text
        text += f"- {get_now()}\n"
        form = UpdateBlogForm(text=text, token="")
        form.update(blog)
        update_blog(blog)
        logger.info("update_home: successfully")
    else:
        logger.error("update_home: home not exists")


def update_blog_content():
    template = Template(
        """{% for blog in blogs %}
- {{ blog.create_at }} [{{ blog.title }}](/blog/{{ blog.id }}/{{ blog.slug }})
{% endfor %}
"""
    )
    blogs = get_blogs_sorted_by_id()
    for blog in blogs:
        blog.create_at = blog.create_at.astimezone(tz=timezone(timedelta(hours=8)))
        blog.update_at = blog.update_at.astimezone(tz=timezone(timedelta(hours=8)))
    text = template.render(blogs=blogs)
    blog = get_blog(2)
    if blog:
        blog.text = text
        update_blog(blog)
        logger.info("update_blog_content: successfully")
    else:
        logger.error("update_blog_content: blog(id=2) not exists")
