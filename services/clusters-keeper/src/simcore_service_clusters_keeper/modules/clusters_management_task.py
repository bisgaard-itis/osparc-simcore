import json
import logging
from collections.abc import Awaitable, Callable

from common_library.async_tools import cancel_wait_task
from fastapi import FastAPI
from servicelib.background_task import create_periodic_task
from servicelib.redis import exclusive

from .._meta import APP_NAME
from ..core.settings import ApplicationSettings
from ..modules.redis import get_redis_client
from .clusters_management_core import check_clusters

_TASK_NAME = "Clusters-keeper EC2 instances management"

logger = logging.getLogger(__name__)


def on_app_startup(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def _startup() -> None:
        app_settings: ApplicationSettings = app.state.settings

        lock_key = f"{APP_NAME}:clusters-management_lock"
        lock_value = json.dumps({})
        app.state.clusters_cleaning_task = create_periodic_task(
            exclusive(get_redis_client(app), lock_key=lock_key, lock_value=lock_value)(
                check_clusters
            ),
            interval=app_settings.CLUSTERS_KEEPER_TASK_INTERVAL,
            task_name=_TASK_NAME,
            app=app,
        )

    return _startup


def on_app_shutdown(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def _stop() -> None:
        await cancel_wait_task(app.state.clusters_cleaning_task, max_delay=5)

    return _stop


def setup(app: FastAPI):
    app_settings: ApplicationSettings = app.state.settings
    if any(
        s is None
        for s in [
            app_settings.CLUSTERS_KEEPER_EC2_ACCESS,
            app_settings.CLUSTERS_KEEPER_PRIMARY_EC2_INSTANCES,
            app_settings.CLUSTERS_KEEPER_SSM_ACCESS,
        ]
    ):
        logger.warning(
            "the clusters management background task is disabled by settings, nothing will happen!"
        )
        return
    app.add_event_handler("startup", on_app_startup(app))
    app.add_event_handler("shutdown", on_app_shutdown(app))
