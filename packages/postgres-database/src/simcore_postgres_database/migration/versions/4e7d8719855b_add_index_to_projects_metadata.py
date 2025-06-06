"""add index to projects_metadata

Revision ID: 4e7d8719855b
Revises: ba9c4816a31b
Create Date: 2025-05-21 11:48:34.062860+00:00

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4e7d8719855b"
down_revision = "ba9c4816a31b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "idx_projects_metadata_root_parent_project_uuid",
        "projects_metadata",
        ["root_parent_project_uuid"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "idx_projects_metadata_root_parent_project_uuid", table_name="projects_metadata"
    )
    # ### end Alembic commands ###
