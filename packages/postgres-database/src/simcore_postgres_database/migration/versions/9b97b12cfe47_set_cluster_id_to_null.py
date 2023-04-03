"""set cluster id to null

Revision ID: 9b97b12cfe47
Revises: 9014ae5fd6e5
Create Date: 2023-03-28 10:20:20.670233+00:00

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "9b97b12cfe47"
down_revision = "9014ae5fd6e5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_comp_runs_cluster_id_clusters", "comp_runs", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_comp_runs_cluster_id_clusters",
        "comp_runs",
        "clusters",
        ["cluster_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_comp_runs_cluster_id_clusters", "comp_runs", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk_comp_runs_cluster_id_clusters",
        "comp_runs",
        "clusters",
        ["cluster_id"],
        ["id"],
        onupdate="CASCADE",
    )
    # ### end Alembic commands ###