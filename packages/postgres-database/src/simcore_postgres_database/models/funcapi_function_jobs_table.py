"""Function jobs table

- List of function jobs served by the simcore platform
"""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

from ._common import RefActions, column_created_datetime, column_modified_datetime
from .base import metadata
from .funcapi_functions_table import functions_table

function_jobs_table = sa.Table(
    "funcapi_function_jobs",
    metadata,
    sa.Column(
        "uuid",
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        doc="Unique id of the function job",
    ),
    sa.Column(
        "title",
        sa.String,
        doc="Name of the function job",
    ),
    sa.Column(
        "description",
        sa.String,
        doc="Description of the function job",
    ),
    sa.Column(
        "function_uuid",
        sa.ForeignKey(
            functions_table.c.uuid,
            onupdate=RefActions.CASCADE,
            ondelete=RefActions.CASCADE,
            name="fk_function_jobs_to_function_uuid",
        ),
        nullable=False,
        index=True,
        doc="Unique identifier of the function",
    ),
    sa.Column(
        "function_class",
        sa.String,
        doc="Class of the function",
    ),
    sa.Column(
        "status",
        sa.String,
        doc="Status of the function job",
    ),
    sa.Column(
        "inputs",
        JSONB,
        doc="Inputs of the function job",
    ),
    sa.Column(
        "outputs",
        JSONB,
        doc="Outputs of the function job",
    ),
    sa.Column(
        "class_specific_data",
        JSONB,
        nullable=True,
        doc="Fields specific for a function class",
    ),
    column_created_datetime(),
    column_modified_datetime(),
    sa.PrimaryKeyConstraint("uuid", name="funcapi_function_jobs_pk"),
)
