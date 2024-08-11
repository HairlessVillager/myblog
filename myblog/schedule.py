"""source: https://github.com/agronholm/apscheduler/blob/master/examples/web/asgi_fastapi.py"""

from __future__ import annotations

from typing import Any, Callable, List, Tuple, Dict
from os import getenv

from fastapi.middleware import Middleware
from sqlalchemy.ext.asyncio import create_async_engine
from starlette.types import ASGIApp, Receive, Scope, Send
from apscheduler import AsyncScheduler
from apscheduler.abc import Trigger
from apscheduler._enums import ConflictPolicy
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.eventbrokers.asyncpg import AsyncpgEventBroker


class SchedulerMiddleware:
    scheduleds: List[Tuple[Callable, Trigger, Dict[str, Any]]] = []

    def __init__(
        self,
        app: ASGIApp,
        scheduler: AsyncScheduler,
    ) -> None:
        self.app = app
        self.scheduler = scheduler

    @classmethod
    def register(
        cls, trigger: Trigger, **add_schedule_kwargs: Dict[str, Any]
    ) -> Callable:
        add_schedule_kwargs.setdefault("conflict_policy", ConflictPolicy.replace)

        def decorator(func: Callable):
            add_schedule_kwargs.setdefault("id", func.__name__)

            cls.scheduleds.append((func, trigger, add_schedule_kwargs))
            return func

        return decorator

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            async with self.scheduler:
                for func, trigger, add_schedule_kwargs in self.scheduleds:
                    await self.scheduler.add_schedule(
                        func, trigger, **add_schedule_kwargs
                    )
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)


def get_middleware():
    engine = create_async_engine(getenv("DB_URL_ASYNC"))
    data_store = SQLAlchemyDataStore(engine)
    event_broker = AsyncpgEventBroker.from_async_sqla_engine(engine)
    scheduler = AsyncScheduler(data_store, event_broker)
    middleware = Middleware(SchedulerMiddleware, scheduler=scheduler)
    return middleware
