import sqlalchemy as sa

from ._common import column_created_datetime, column_modified_datetime
from .base import metadata
from .projects import projects

projects_to_api_server_jobs = sa.Table(
    "projects_to_api_server_jobs",
    metadata,
    sa.Column(
        "project_uuid",
        sa.String,
        sa.ForeignKey(
            projects.c.uuid,
            name="project_uuid",
        ),
        index=True,
        nullable=False,
        doc="Project UUID",
    ),
    sa.Column(
        "job_id",
        sa.String,
        nullable=False,
        primary_key=True,
        unique=True,
        doc="Characterizes the job from the POV of the api server",
    ),
    sa.Column(
        "solver_key",
        sa.String,
        nullable=True,
        doc="Solver key",
    ),
    sa.Column(
        "solver_version",
        sa.String,
        nullable=True,
        doc="MAJOR.MINOR.PATCH semantic versioning (see https://semver.org)",
    ),
    column_created_datetime(timezone=True),
    column_modified_datetime(timezone=True),
)
