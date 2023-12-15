import logging

from aiohttp import web
from aiohttp_security import login_required
from servicelib.aiohttp.requests_validation import parse_request_query_parameters_as
from simcore_service_webserver.security.decorators import permission_required

from .._meta import API_VTAG as VTAG
from ._api_server_jobs_models import JobCreateParams
from ._common_models import RequestContext

_logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.post(f"/{VTAG}/projects/{{project_id}}/jobs", name="create_job")
@login_required
@permission_required("project.create")
async def create_job(request: web.Request) -> ApiServerJobGet:
    req_ctx = RequestContext.parse_obj(request)
    query_params = parse_request_query_parameters_as(JobCreateParams, request)
