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
            name="fk_projects_comments_project_uuid",
            ondelete="CASCADE",
            onupdate="CASCADE",
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
        "parent",
        sa.String,
        nullable=False,
        primary_key=True,
        unique=True,
        doc="The parent resource of the job from the POV of the api server (https://cloud.google.com/apis/design/standard_fields)",
    ),
    column_created_datetime(timezone=True),
    column_modified_datetime(timezone=True),
)
