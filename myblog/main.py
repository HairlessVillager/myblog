import logging

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .task import update_blog_content
from .model import (
    Blog,
    CreateBlogForm,
    UpdateBlogForm,
)
from .query import (
    create_blog,
    get_blog,
    update_blog,
)
from .auth import (
    check_token,
)
from .util import (
    blog2md,
    md2html,
)

app = FastAPI()
logger = logging.getLogger("app")


@app.get("/")
async def home_html():
    return RedirectResponse(url="/blog/1/home")


@app.get("/blog/404-not-found")
async def blog_404_not_found():
    blog = Blog(
        title="404 Not Found",
        pinned=False,
        deleted=False,
        slug="404-not-found",
        create_at=None,
        update_at=None,
        text="*this page intentionally left blank*",
    )
    md = await blog2md(blog)
    html = md2html(md)
    return HTMLResponse(html)


@app.get("/blog/{id}")
async def blog_redirect(id: int):
    blog = await get_blog(id)
    if blog:
        return RedirectResponse(url=f"/blog/{blog.id}/{blog.slug}")
    else:
        return RedirectResponse(url="/blog/404-not-found")


@app.get("/blog/{id}/{slug}")
async def blog_html(id: int, slug: str):
    logger.debug("get request")
    blog = await get_blog(id)
    logger.debug("get blog")
    if blog:
        if slug != blog.slug:
            return RedirectResponse(f"/blog/{id}/{blog.slug}")
        logger.debug("slug checked")
        if blog.html:
            logger.debug("blog have html")
            return HTMLResponse(blog.html)
        else:
            logger.debug("blog does not have html")
            md = await blog2md(blog)
            logger.debug("blog -> md")
            html = md2html(md)
            logger.debug("md -> html")
            blog.html = html
            await update_blog(blog)
            logger.debug("blog saved")
            return HTMLResponse(html)
    else:
        return RedirectResponse("/blog/404-not-found")


@app.post("/blog/edit/{id}")
async def blog_update_api(
    id: int,
    form: UpdateBlogForm,
    background_tasks: BackgroundTasks,
):
    if check_token(form.token):
        blog = await get_blog(id)
        if blog:
            form.update(blog)
            await update_blog(blog)
            background_tasks.add_task(update_blog_content)
            msg = f"blog {id} updated"
            logger.info(msg)
            return {"status": "ok", "msg": msg}
        else:
            return {"status": "error", "msg": f"blog {id} not found"}
    else:
        return {"status": "error", "msg": "token timeout"}


@app.post("/blog/new")
async def blog_new_api(
    form: CreateBlogForm,
    background_tasks: BackgroundTasks,
):
    if check_token(form.token):
        blog = form.to_blog()
        id = await create_blog(blog)
        background_tasks.add_task(update_blog_content)
        msg = f"new blog id: {id}"
        logger.info(msg)
        return {"status": "ok", "msg": msg}
    else:
        return {"status": "error", "msg": "token timeout"}


@app.get("/favicon.ico")
async def favicon_ico():
    return RedirectResponse("/static/favicon.ico")
