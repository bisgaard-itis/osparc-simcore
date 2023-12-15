from typing import TypeAlias
from uuid import UUID

from models_library.basic_types import VersionStr
from models_library.projects import ProjectID
from models_library.services import COMPUTATIONAL_SERVICE_KEY_RE
from pydantic import BaseModel, ConstrainedStr

JobID: TypeAlias = UUID


class SolverKeyId(ConstrainedStr):
    strip_whitespace = True
    regex = COMPUTATIONAL_SERVICE_KEY_RE


class JobRow(BaseModel):
    project_id: ProjectID
    job_id: JobID
    solver_key: SolverKeyId
    solver_version: VersionStr
