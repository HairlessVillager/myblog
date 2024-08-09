# TODO: refactor with a argpaser
# TODO: reuse .auth
from datetime import datetime
from pathlib import Path
from argparse import ArgumentParser

import requests

from myblog.auth import create_token


def create(args):
    dt = datetime.now()
    token = create_token(dt)
    print(f"{dt=}, {token=}")
    resp = requests.post(
        f"http://{args.domain}/blog/new",
        json={
            "title": args.title,
            "pinned": args.pinned,
            "deleted": args.deleted,
            "slug": args.slug,
            "text": args.file.read_text(encoding=args.encoding),
            "token": token,
        },
    )
    print(resp.text)


def update(args):
    dt = datetime.now()
    token = create_token(dt)
    print(f"{dt=}, {token=}")
    json = {
        "title": args.title,
        "pinned": args.pinned,
        "deleted": args.deleted,
        "slug": args.slug,
        "text": args.file.read_text(encoding=args.encoding),
        "token": token,
    }
    resp = requests.post(
        f"http://{args.domain}/blog/edit/{args.id}",
        json={k: v for k, v in json.items() if v},
    )
    print(resp.text)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="myblog",
        description="a tool to sync blogs between local and website",
    )
    subparsers = parser.add_subparsers()
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    parser_create = subparsers.add_parser("create", help="create a blog")
    parser_create.add_argument("domain", type=str, default="127.0.0.1:8000")
    parser_create.add_argument("file", type=Path)
    parser_create.add_argument("--title", type=str, required=True)
    parser_create.add_argument("--slug", type=str, required=True)
    parser_create.add_argument("--pinned", type=bool, default=False)
    parser_create.add_argument("--deleted", type=bool, default=False)
    parser_create.add_argument("--encoding", type=str, default="utf-8")
    parser_create.set_defaults(func=create)

    parser_update = subparsers.add_parser("update", help="update a blog")
    parser_update.add_argument("domain", type=str, default="127.0.0.1:8000")
    parser_update.add_argument("id", type=int)
    parser_update.add_argument("file", type=Path)
    parser_update.add_argument("--title", type=str, required=False)
    parser_update.add_argument("--slug", type=str, required=False)
    parser_update.add_argument("--pinned", type=bool, required=False)
    parser_update.add_argument("--deleted", type=bool, required=False)
    parser_update.add_argument("--encoding", type=str, default="utf-8")
    parser_update.set_defaults(func=update)

    args = parser.parse_args()
    args.func(args)
