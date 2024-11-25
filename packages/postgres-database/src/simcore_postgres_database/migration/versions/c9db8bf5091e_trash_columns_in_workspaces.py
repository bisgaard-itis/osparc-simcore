"""trash columns in workspaces

Revision ID: c9db8bf5091e
Revises: 8e1f83486be7
Create Date: 2024-11-20 16:42:43.784855+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c9db8bf5091e"
down_revision = "8e1f83486be7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "workspaces",
        sa.Column(
            "trashed",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="The date and time when the workspace was marked as trashed. Null if the workspace has not been trashed [default].",
        ),
    )
    op.add_column(
        "workspaces",
        sa.Column(
            "trashed_by",
            sa.BigInteger(),
            nullable=True,
            comment="User who trashed the workspace, or null if not trashed or user is unknown.",
        ),
    )
    op.create_foreign_key(
        "fk_workspace_trashed_by_user_id",
        "workspaces",
        "users",
        ["trashed_by"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_workspace_trashed_by_user_id", "workspaces", type_="foreignkey"
    )
    op.drop_column("workspaces", "trashed_by")
    op.drop_column("workspaces", "trashed")
    # ### end Alembic commands ###