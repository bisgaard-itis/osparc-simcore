""" Operations on dynamic-services

- This interface HIDES request/responses/exceptions to the director-v2 API service

"""

import logging

from aiohttp import web
from models_library.projects import ProjectID
from pydantic import NonNegativeInt
from servicelib.logging_utils import log_decorator
from yarl import URL

from ._core_base import DataType, request_director_v2
from .settings import DirectorV2Settings, get_plugin_settings

_log = logging.getLogger(__name__)


@log_decorator(logger=_log)
async def get_project_inactivity(
    app: web.Application,
    project_id: ProjectID,
    max_inactivity_seconds: NonNegativeInt,
) -> DataType:
    settings: DirectorV2Settings = get_plugin_settings(app)
    backend_url = (
        URL(settings.base_url) / f"dynamic_services/projects/{project_id}/inactivity"
    ).update_query(max_inactivity_seconds=max_inactivity_seconds)
    result = await request_director_v2(
        app, "GET", backend_url, expected_status=web.HTTPOk
    )
    assert isinstance(result, dict)  # nosec
    return result
