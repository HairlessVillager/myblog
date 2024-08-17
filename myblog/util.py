from datetime import timezone, timedelta
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
from jinja2 import Template

from .model import (
    Blog,
)


async def blog2md(blog: Blog) -> str:
    from .query import get_pinned_blogs_sorted_by_id

    blog.create_at = blog.create_at.astimezone(tz=timezone(timedelta(hours=8)))
    blog.update_at = blog.update_at.astimezone(tz=timezone(timedelta(hours=8)))
    template = Template(
        """### HairlessVillager's Blog

---

**pinned**
{% for blog in pinned_blogs %}
- [{{ blog.title }}](/blog/{{ blog.id }}/{{ blog.slug }})
{% endfor %}

---

# {{ blog.title }}

- *create@{{ blog.create_at }}*
- *update@{{ blog.update_at }}*

---

{{ blog.text }}
"""
    )
    md = template.render(pinned_blogs=await get_pinned_blogs_sorted_by_id(), blog=blog)
    return md


def md2html(md: str) -> str:
    mdit = (
        MarkdownIt("commonmark", {"breaks": True, "html": True})
        .use(front_matter_plugin)
        .use(footnote_plugin)
        .enable("table")
    )
    return mdit.render(md)
