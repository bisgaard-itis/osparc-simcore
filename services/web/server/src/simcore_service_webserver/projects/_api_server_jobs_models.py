from models_library.basic_types import VersionStr
from pydantic import BaseModel
from simcore_service_api_server.models.schemas.solvers import SolverKeyId


class JobCreateParams(BaseModel):
    solver: SolverKeyId
    version: VersionStr
