import logging

from fastapi import FastAPI
from servicelib.fastapi.tracing import (
    initialize_fastapi_app_tracing,
    setup_tracing,
)

from .._meta import (
    API_VERSION,
    API_VTAG,
    APP_FINISHED_BANNER_MSG,
    APP_NAME,
    APP_STARTED_BANNER_MSG,
    APP_STARTED_COMPUTATIONAL_BANNER_MSG,
    APP_STARTED_DISABLED_BANNER_MSG,
    APP_STARTED_DYNAMIC_BANNER_MSG,
)
from ..api.routes import setup_api_routes
from ..modules.cluster_scaling.auto_scaling_task import (
    setup as setup_auto_scaler_background_task,
)
from ..modules.cluster_scaling.warm_buffer_machines_pool_task import (
    setup as setup_warm_buffer_machines_pool_task,
)
from ..modules.docker import setup as setup_docker
from ..modules.ec2 import setup as setup_ec2
from ..modules.instrumentation import setup as setup_instrumentation
from ..modules.rabbitmq import setup as setup_rabbitmq
from ..modules.redis import setup as setup_redis
from ..modules.ssm import setup as setup_ssm
from .settings import ApplicationSettings

logger = logging.getLogger(__name__)


def create_app(settings: ApplicationSettings) -> FastAPI:
    app = FastAPI(
        debug=settings.AUTOSCALING_DEBUG,
        title=APP_NAME,
        description="Service to auto-scale swarm",
        version=API_VERSION,
        openapi_url=f"/api/{API_VTAG}/openapi.json",
        docs_url="/dev/doc",
        redoc_url=None,  # default disabled
    )
    # STATE
    app.state.settings = settings
    assert app.state.settings.API_VERSION == API_VERSION  # nosec

    # PLUGINS SETUP
    if app.state.settings.AUTOSCALING_TRACING:
        setup_tracing(app, app.state.settings.AUTOSCALING_TRACING, APP_NAME)

    setup_instrumentation(app)
    setup_api_routes(app)
    setup_docker(app)
    setup_rabbitmq(app)
    setup_ec2(app)
    setup_ssm(app)
    setup_redis(app)

    if app.state.settings.AUTOSCALING_TRACING:
        initialize_fastapi_app_tracing(app)

    setup_auto_scaler_background_task(app)
    setup_warm_buffer_machines_pool_task(app)

    # ERROR HANDLERS

    # EVENTS
    async def _on_startup() -> None:
        print(APP_STARTED_BANNER_MSG, flush=True)  # noqa: T201
        if settings.AUTOSCALING_NODES_MONITORING:
            print(APP_STARTED_DYNAMIC_BANNER_MSG, flush=True)  # noqa: T201
        elif settings.AUTOSCALING_DASK:
            print(APP_STARTED_COMPUTATIONAL_BANNER_MSG, flush=True)  # noqa: T201
        else:
            print(APP_STARTED_DISABLED_BANNER_MSG, flush=True)  # noqa: T201

    async def _on_shutdown() -> None:
        print(APP_FINISHED_BANNER_MSG, flush=True)  # noqa: T201

    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)

    return app
