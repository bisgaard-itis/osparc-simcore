# pylint: disable=too-many-arguments

import logging
from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models_library.clusters import ClusterID
from models_library.projects import ProjectID
from models_library.projects_nodes_io import NodeID
from pydantic.types import PositiveInt

from ..._service import create_solver_or_program_job
from ...exceptions.backend_errors import ProjectAlreadyStartedError
from ...exceptions.service_errors_utils import DEFAULT_BACKEND_SERVICE_STATUS_CODES
from ...models.basic_types import VersionStr
from ...models.schemas.errors import ErrorGet
from ...models.schemas.jobs import (
    Job,
    JobID,
    JobInputs,
    JobMetadata,
    JobMetadataUpdate,
    JobStatus,
)
from ...models.schemas.solvers import Solver, SolverKeyId
from ...services_http.catalog import CatalogApi
from ...services_http.director_v2 import DirectorV2Api
from ...services_http.jobs import replace_custom_metadata, start_project, stop_project
from ...services_http.solver_job_models_converters import (
    create_jobstatus_from_task,
)
from ...services_rpc.wb_api_server import WbApiRpcClient
from ..dependencies.application import get_reverse_url_mapper
from ..dependencies.authentication import get_current_user_id, get_product_name
from ..dependencies.services import get_api_client
from ..dependencies.webserver_http import AuthSession, get_webserver_session
from ..dependencies.webserver_rpc import (
    get_wb_api_rpc_client,
)
from ._constants import (
    FMSG_CHANGELOG_ADDED_IN_VERSION,
    FMSG_CHANGELOG_CHANGED_IN_VERSION,
    FMSG_CHANGELOG_NEW_IN_VERSION,
)

_logger = logging.getLogger(__name__)

router = APIRouter()


def _compose_job_resource_name(solver_key, solver_version, job_id) -> str:
    """Creates a unique resource name for solver's jobs"""
    return Job.compose_resource_name(
        parent_name=Solver.compose_resource_name(solver_key, solver_version),
        job_id=job_id,
    )


# JOBS ---------------
#
# - Similar to docker container's API design (container = job and image = solver)
#
METADATA_STATUS_CODES: dict[int | str, dict[str, Any]] = {
    status.HTTP_404_NOT_FOUND: {
        "description": "Metadata not found",
        "model": ErrorGet,
    },
    **DEFAULT_BACKEND_SERVICE_STATUS_CODES,
}

JOBS_STATUS_CODES: dict[int | str, dict[str, Any]] = {
    status.HTTP_402_PAYMENT_REQUIRED: {
        "description": "Payment required",
        "model": ErrorGet,
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Job/wallet/pricing details not found",
        "model": ErrorGet,
    },
    **DEFAULT_BACKEND_SERVICE_STATUS_CODES,
}


@router.post(
    "/{solver_key:path}/releases/{version}/jobs",
    response_model=Job,
    status_code=status.HTTP_201_CREATED,
    responses=JOBS_STATUS_CODES,
)
async def create_solver_job(
    solver_key: SolverKeyId,
    version: VersionStr,
    inputs: JobInputs,
    user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
    catalog_client: Annotated[CatalogApi, Depends(get_api_client(CatalogApi))],
    webserver_api: Annotated[AuthSession, Depends(get_webserver_session)],
    wb_api_rpc: Annotated[WbApiRpcClient, Depends(get_wb_api_rpc_client)],
    url_for: Annotated[Callable, Depends(get_reverse_url_mapper)],
    product_name: Annotated[str, Depends(get_product_name)],
    hidden: Annotated[bool, Query()] = True,
    x_simcore_parent_project_uuid: Annotated[ProjectID | None, Header()] = None,
    x_simcore_parent_node_id: Annotated[NodeID | None, Header()] = None,
):
    """Creates a job in a specific release with given inputs.

    NOTE: This operation does **not** start the job
    """

    # ensures user has access to solver
    solver = await catalog_client.get_solver(
        user_id=user_id,
        name=solver_key,
        version=version,
        product_name=product_name,
    )
    job, project = await create_solver_or_program_job(
        webserver_api=webserver_api,
        solver_or_program=solver,
        inputs=inputs,
        url_for=url_for,
        hidden=hidden,
        parent_project_uuid=x_simcore_parent_project_uuid,
        parent_node_id=x_simcore_parent_node_id,
    )

    await wb_api_rpc.mark_project_as_job(
        product_name=product_name,
        user_id=user_id,
        project_uuid=project.uuid,
        job_parent_resource_name=job.runner_name,
    )
    return job


@router.delete(
    "/{solver_key:path}/releases/{version}/jobs/{job_id:uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=JOBS_STATUS_CODES,
    description="Deletes an existing solver job\n\n"
    + FMSG_CHANGELOG_NEW_IN_VERSION.format("0.7"),
)
async def delete_job(
    solver_key: SolverKeyId,
    version: VersionStr,
    job_id: JobID,
    webserver_api: Annotated[AuthSession, Depends(get_webserver_session)],
):
    job_name = _compose_job_resource_name(solver_key, version, job_id)
    _logger.debug("Deleting Job '%s'", job_name)

    await webserver_api.delete_project(project_id=job_id)


@router.post(
    "/{solver_key:path}/releases/{version}/jobs/{job_id:uuid}:start",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobStatus,
    responses=JOBS_STATUS_CODES
    | {
        status.HTTP_200_OK: {
            "description": "Job already started",
            "model": JobStatus,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Cluster not found",
            "model": ErrorGet,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Configuration error",
            "model": ErrorGet,
        },
    },
    description="Starts job job_id created with the solver solver_key:version\n\n"
    + FMSG_CHANGELOG_ADDED_IN_VERSION.format("0.4.3", "query parameter `cluster_id`")
    + FMSG_CHANGELOG_ADDED_IN_VERSION.format(
        "0.6", "responds with a 202 when successfully starting a computation"
    )
    + FMSG_CHANGELOG_CHANGED_IN_VERSION.format(
        "0.8", "query parameter `cluster_id` deprecated"
    ),
)
async def start_job(
    request: Request,
    solver_key: SolverKeyId,
    version: VersionStr,
    job_id: JobID,
    user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
    director2_api: Annotated[DirectorV2Api, Depends(get_api_client(DirectorV2Api))],
    webserver_api: Annotated[AuthSession, Depends(get_webserver_session)],
    cluster_id: Annotated[  # pylint: disable=unused-argument  # noqa: ARG001
        ClusterID | None, Query(deprecated=True)
    ] = None,
):
    job_name = _compose_job_resource_name(solver_key, version, job_id)
    _logger.debug("Start Job '%s'", job_name)

    try:
        await start_project(
            request=request,
            job_id=job_id,
            expected_job_name=job_name,
            webserver_api=webserver_api,
        )
    except ProjectAlreadyStartedError:
        job_status = await inspect_job(
            solver_key=solver_key,
            version=version,
            job_id=job_id,
            user_id=user_id,
            director2_api=director2_api,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(job_status)
        )
    return await inspect_job(
        solver_key=solver_key,
        version=version,
        job_id=job_id,
        user_id=user_id,
        director2_api=director2_api,
    )


@router.post(
    "/{solver_key:path}/releases/{version}/jobs/{job_id:uuid}:stop",
    response_model=JobStatus,
    responses=JOBS_STATUS_CODES,
)
async def stop_job(
    solver_key: SolverKeyId,
    version: VersionStr,
    job_id: JobID,
    user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
    director2_api: Annotated[DirectorV2Api, Depends(get_api_client(DirectorV2Api))],
):
    job_name = _compose_job_resource_name(solver_key, version, job_id)
    _logger.debug("Stopping Job '%s'", job_name)

    return await stop_project(
        job_id=job_id, user_id=user_id, director2_api=director2_api
    )


@router.post(
    "/{solver_key:path}/releases/{version}/jobs/{job_id:uuid}:inspect",
    response_model=JobStatus,
    responses=JOBS_STATUS_CODES,
)
async def inspect_job(
    solver_key: SolverKeyId,
    version: VersionStr,
    job_id: JobID,
    user_id: Annotated[PositiveInt, Depends(get_current_user_id)],
    director2_api: Annotated[DirectorV2Api, Depends(get_api_client(DirectorV2Api))],
) -> JobStatus:
    job_name = _compose_job_resource_name(solver_key, version, job_id)
    _logger.debug("Inspecting Job '%s'", job_name)

    task = await director2_api.get_computation(project_id=job_id, user_id=user_id)
    job_status: JobStatus = create_jobstatus_from_task(task)
    return job_status


@router.patch(
    "/{solver_key:path}/releases/{version}/jobs/{job_id:uuid}/metadata",
    response_model=JobMetadata,
    responses=METADATA_STATUS_CODES,
    description="Updates custom metadata from a job\n\n"
    + FMSG_CHANGELOG_NEW_IN_VERSION.format("0.7"),
)
async def replace_job_custom_metadata(
    solver_key: SolverKeyId,
    version: VersionStr,
    job_id: JobID,
    update: JobMetadataUpdate,
    webserver_api: Annotated[AuthSession, Depends(get_webserver_session)],
    url_for: Annotated[Callable, Depends(get_reverse_url_mapper)],
):
    job_name = _compose_job_resource_name(solver_key, version, job_id)
    _logger.debug("Custom metadata for '%s'", job_name)

    return await replace_custom_metadata(
        job_name=job_name,
        job_id=job_id,
        update=update,
        webserver_api=webserver_api,
        self_url=url_for(
            "replace_job_custom_metadata",
            solver_key=solver_key,
            version=version,
            job_id=job_id,
        ),
    )
