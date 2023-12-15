"""add projects_to_api_server_jobs table

Revision ID: 65b0b4386373
Revises: 0ad000429e3d
Create Date: 2023-12-15 08:53:34.257538+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "65b0b4386373"
down_revision = "0ad000429e3d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects_to_api_server_jobs",
        sa.Column("project_uuid", sa.String(), nullable=False),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("solver_key", sa.String(), nullable=True),
        sa.Column("solver_version", sa.String(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "modified",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_uuid"], ["projects.uuid"], name="project_uuid"
        ),
        sa.PrimaryKeyConstraint("job_id"),
        sa.UniqueConstraint("job_id"),
    )
    op.create_index(
        op.f("ix_projects_to_api_server_jobs_project_uuid"),
        "projects_to_api_server_jobs",
        ["project_uuid"],
        unique=False,
    )
    op.execute(
        sa.DDL(
            f"""
INSERT INTO projects_to_api_server_jobs (project_uuid, job_id, solver_key, solver_version)
SELECT uuid, uuid, replace(substring(name from 'solvers/(.*)/releases'), '%2F', '/'), substring(name from 'releases/(.*)/jobs')
FROM projects
WHERE name ~ 'simcore%2Fservices%2Fcomp%2F.*/releases/.*/jobs/.*'
"""
        )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_projects_to_api_server_jobs_project_uuid"),
        table_name="projects_to_api_server_jobs",
    )
    op.drop_table("projects_to_api_server_jobs")
    # ### end Alembic commands ###
