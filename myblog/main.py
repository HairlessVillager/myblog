from os import getenv
import logging
from datetime import timedelta, timezone

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
from jinja2 import Template

from .task import update_blog_content
from .model import (
    Blog,
    CreateBlogForm,
    UpdateBlogForm,
)
from .query import (
    create_blog,
    get_blog,
    get_pinned_blogs_sorted_by_id,
    update_blog,
)
from .auth import (
    check_token,
)
from .schedule import (
    get_middleware,
)

app = FastAPI(middleware=[get_middleware()])
logger = logging.getLogger("app")


def blog2md(blog: Blog) -> str:
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
    md = template.render(pinned_blogs=get_pinned_blogs_sorted_by_id(), blog=blog)
    return md


def md2html(md: str) -> str:
    mdit = (
        MarkdownIt("commonmark", {"breaks": True, "html": True})
        .use(front_matter_plugin)
        .use(footnote_plugin)
        .enable("table")
    )
    return mdit.render(md)


@app.on_event("startup")
def startup_event():
    from .model import SqlalchemyBase, engine

    # create all tables
    if getenv("DROP_ALL"):
        SqlalchemyBase.metadata.drop_all(engine)
        logger.warning("startup_event: dropped all tables")
    SqlalchemyBase.metadata.create_all(engine)
    logger.info("startup_event: created all tables")

    # init home page
    blog = get_blog(1)
    if blog:
        form = UpdateBlogForm(token="")
        form.update(blog)
        update_blog(blog)
        logger.info("startup_event: home updated")
    else:
        form = CreateBlogForm(
            title="Home",
            pinned=True,
            deleted=False,
            slug="home",
            text="*this page intentionally left blank*",
            token="",
        )
        blog = form.to_blog()
        create_blog(blog)
        logger.info("startup_event: home created")

    # init blog content page
    blog = get_blog(2)
    if blog:
        form = UpdateBlogForm(token="")
        form.update(blog)
        update_blog(blog)
        logger.info("startup_event: blog content updated")
    else:
        form = CreateBlogForm(
            title="Blog Content",
            pinned=True,
            deleted=False,
            slug="blog-content",
            text="*this page intentionally left blank*",
            token="",
        )
        blog = form.to_blog()
        create_blog(blog)
        logger.info("startup_event: blog content created")

    # update blog content
    update_blog_content()
    logger.info("startup_event: update blog content successfully")

    # mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("startup_event: mount static files successfully")


@app.get("/")
def home_html():
    return RedirectResponse(url="/blog/1/home")


@app.get("/blog/404-not-found")
def blog_404_not_found():
    blog = Blog(
        title="404 Not Found",
        pinned=False,
        deleted=False,
        slug="404-not-found",
        create_at=None,
        update_at=None,
        text="*this page intentionally left blank*",
    )
    md = blog2md(blog)
    html = md2html(md)
    return HTMLResponse(html)


@app.get("/blog/{id}")
def blog_redirect(id: int):
    blog = get_blog(id)
    if blog:
        return RedirectResponse(url=f"/blog/{blog.id}/{blog.slug}")
    else:
        return RedirectResponse(url="/blog/404-not-found")


@app.get("/blog/{id}/{slug}")
def blog_html(id: int, slug: str):
    blog = get_blog(id)
    if blog:
        if slug != blog.slug:
            return RedirectResponse(f"/blog/{id}/{blog.slug}")
        md = blog2md(blog)
        html = md2html(md)
        return HTMLResponse(html)
    else:
        return RedirectResponse("/blog/404-not-found")


@app.post("/blog/edit/{id}")
def blog_update_api(
    id: int,
    form: UpdateBlogForm,
    background_tasks: BackgroundTasks,
):
    if check_token(form.token):
        blog = get_blog(id)
        if blog:
            form.update(blog)
            update_blog(blog)
            background_tasks.add_task(update_blog_content)
            msg = f"blog {id} updated"
            logger.info(msg)
            return {"status": "ok", "msg": msg}
        else:
            return {"status": "error", "msg": f"blog {id} not found"}
    else:
        return {"status": "error", "msg": "token timeout"}


@app.post("/blog/new")
def blog_new_api(
    form: CreateBlogForm,
    background_tasks: BackgroundTasks,
):
    if check_token(form.token):
        blog = form.to_blog()
        id = create_blog(blog)
        background_tasks.add_task(update_blog_content)
        msg = f"new blog id: {id}"
        logger.info(msg)
        return {"status": "ok", "msg": msg}
    else:
        return {"status": "error", "msg": "token timeout"}


@app.get("/favicon.ico")
def favicon_ico():
    return RedirectResponse("/static/favicon.ico")
