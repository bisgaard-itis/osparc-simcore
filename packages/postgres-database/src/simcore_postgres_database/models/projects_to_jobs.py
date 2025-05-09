import sqlalchemy as sa

from ._common import RefActions
from .base import metadata
from .projects import projects

projects_to_jobs = sa.Table(
    # Maps projects used as jobs in the public-api
    "projects_to_jobs",
    metadata,
    sa.Column(
        "project_uuid",
        sa.String,
        sa.ForeignKey(
            projects.c.uuid,
            onupdate=RefActions.CASCADE,
            ondelete=RefActions.CASCADE,
            name="fk_projects_to_jobs_project_uuid",
        ),
        nullable=False,
        doc="Foreign key to projects.uuid",
    ),
    sa.Column(
        "job_parent_resource_name",
        sa.String,
        nullable=False,
        doc="Prefix for the job resource name use in the public-api. For example, if "
        "the relative resource name is shelves/shelf1/jobs/job2, "
        "the parent resource name is shelves/shelf1.",
    ),
    # Composite key (project_uuid, job_parent_resource_name) uniquely identifies very row
    sa.UniqueConstraint(
        "project_uuid",
        "job_parent_resource_name",
        name="uq_projects_to_jobs_project_uuid_job_parent_resource_name",
    ),
)
