from os import getenv
from asyncio import run

from myblog.task import update_blog_content
from myblog.model import (
    CreateBlogForm,
    UpdateBlogForm,
)
from myblog.query import (
    create_blog,
    get_blog,
    update_blog,
)
from myblog.model import (
    SqlalchemyBase,
    engine,
)


async def startup():
    # create all tables
    async with engine.begin() as conn:
        if getenv("DROP_ALL"):
            await conn.run_sync(SqlalchemyBase.metadata.drop_all)
            print("startup_event: dropped all tables")
        await conn.run_sync(SqlalchemyBase.metadata.create_all)
        print("startup_event: created all tables")

    # init home page
    blog = await get_blog(1)
    if blog:
        form = UpdateBlogForm(token="")
        form.update(blog)
        await update_blog(blog)
        print("startup_event: home updated")
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
        await create_blog(blog)
        print("startup_event: home created")

    # init blog content page
    blog = await get_blog(2)
    if blog:
        form = UpdateBlogForm(token="")
        form.update(blog)
        await update_blog(blog)
        print("startup_event: blog content updated")
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
        await create_blog(blog)
        print("startup_event: blog content created")

    # update blog content
    await update_blog_content()
    print("startup_event: update blog content successfully")


if __name__ == "__main__":
    run(startup())
