import logging

from aiohttp import web
from models_library.groups import GroupID
from models_library.projects import ProjectID
from pydantic import BaseModel, ConfigDict
from servicelib.aiohttp import status
from servicelib.aiohttp.requests_validation import (
    parse_request_body_as,
    parse_request_path_parameters_as,
)

from ..._meta import api_version_prefix as VTAG
from ...login.decorators import login_required
from ...security.decorators import permission_required
from ...utils_aiohttp import envelope_json_response
from .. import _groups_service
from .._groups_service import ProjectGroupGet
from ._rest_exceptions import handle_plugin_requests_exceptions
from ._rest_schemas import ProjectPathParams, RequestContext

_logger = logging.getLogger(__name__)


routes = web.RouteTableDef()


class _ProjectsGroupsPathParams(BaseModel):
    project_id: ProjectID
    group_id: GroupID
    model_config = ConfigDict(extra="forbid")


class _ProjectsGroupsBodyParams(BaseModel):
    read: bool
    write: bool
    delete: bool
    model_config = ConfigDict(extra="forbid")


@routes.post(
    f"/{VTAG}/projects/{{project_id}}/groups/{{group_id}}", name="create_project_group"
)
@login_required
@permission_required("project.access_rights.update")
@handle_plugin_requests_exceptions
async def create_project_group(request: web.Request):
    req_ctx = RequestContext.model_validate(request)
    path_params = parse_request_path_parameters_as(_ProjectsGroupsPathParams, request)
    body_params = await parse_request_body_as(_ProjectsGroupsBodyParams, request)

    project_groups: ProjectGroupGet = await _groups_service.create_project_group(
        request.app,
        user_id=req_ctx.user_id,
        project_id=path_params.project_id,
        group_id=path_params.group_id,
        read=body_params.read,
        write=body_params.write,
        delete=body_params.delete,
        product_name=req_ctx.product_name,
    )

    return envelope_json_response(project_groups, web.HTTPCreated)


@routes.get(f"/{VTAG}/projects/{{project_id}}/groups", name="list_project_groups")
@login_required
@permission_required("project.read")
@handle_plugin_requests_exceptions
async def list_project_groups(request: web.Request):
    req_ctx = RequestContext.model_validate(request)
    path_params = parse_request_path_parameters_as(ProjectPathParams, request)

    project_groups: list[ProjectGroupGet] = (
        await _groups_service.list_project_groups_by_user_and_project(
            request.app,
            user_id=req_ctx.user_id,
            project_id=path_params.project_id,
            product_name=req_ctx.product_name,
        )
    )

    return envelope_json_response(project_groups, web.HTTPOk)


@routes.put(
    f"/{VTAG}/projects/{{project_id}}/groups/{{group_id}}",
    name="replace_project_group",
)
@login_required
@permission_required("project.access_rights.update")
@handle_plugin_requests_exceptions
async def replace_project_group(request: web.Request):
    req_ctx = RequestContext.model_validate(request)
    path_params = parse_request_path_parameters_as(_ProjectsGroupsPathParams, request)
    body_params = await parse_request_body_as(_ProjectsGroupsBodyParams, request)

    return await _groups_service.replace_project_group(
        app=request.app,
        user_id=req_ctx.user_id,
        project_id=path_params.project_id,
        group_id=path_params.group_id,
        read=body_params.read,
        write=body_params.write,
        delete=body_params.delete,
        product_name=req_ctx.product_name,
    )


@routes.delete(
    f"/{VTAG}/projects/{{project_id}}/groups/{{group_id}}",
    name="delete_project_group",
)
@login_required
@permission_required("project.access_rights.update")
@handle_plugin_requests_exceptions
async def delete_project_group(request: web.Request):
    req_ctx = RequestContext.model_validate(request)
    path_params = parse_request_path_parameters_as(_ProjectsGroupsPathParams, request)

    await _groups_service.delete_project_group(
        app=request.app,
        user_id=req_ctx.user_id,
        project_id=path_params.project_id,
        group_id=path_params.group_id,
        product_name=req_ctx.product_name,
    )
    return web.json_response(status=status.HTTP_204_NO_CONTENT)
