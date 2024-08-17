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


async def startup():
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
