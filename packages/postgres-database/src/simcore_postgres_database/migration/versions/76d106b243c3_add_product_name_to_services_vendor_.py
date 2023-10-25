"""add product_name to services_vendor_secrets

Revision ID: 76d106b243c3
Revises: 3810966d1534
Create Date: 2023-10-19 14:28:50.637834+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "76d106b243c3"
down_revision = "3810966d1534"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "services_vendor_secrets",
        sa.Column("product_name", sa.String(), server_default="osparc", nullable=False),
    )
    op.create_foreign_key(
        "fk_services_name_products",
        "services_vendor_secrets",
        "products",
        ["product_name"],
        ["name"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###

    op.drop_constraint(
        "services_vendor_secrets_pk", "services_vendor_secrets", type_="primary"
    )
    op.create_primary_key(
        "services_vendor_secrets_pk",
        "services_vendor_secrets",
        ["service_key", "service_base_version", "product_name"],
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_services_name_products", "services_vendor_secrets", type_="foreignkey"
    )
    op.drop_column("services_vendor_secrets", "product_name")
    # ### end Alembic commands ###

    op.create_primary_key(
        "services_vendor_secrets_pk",
        "services_vendor_secrets",
        ["service_key", "service_base_version"],
    )