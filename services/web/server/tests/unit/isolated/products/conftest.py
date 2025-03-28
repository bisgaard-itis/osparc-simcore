# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-variable
# pylint: disable=too-many-arguments


import json
import re
from typing import Any

import pytest
from faker import Faker
from models_library.products import ProductName
from pytest_simcore.helpers.faker_factories import random_product
from simcore_postgres_database.models.products import products as products_table
from sqlalchemy import String
from sqlalchemy.dialects import postgresql


@pytest.fixture
def product_db_server_defaults() -> dict[str, Any]:
    server_defaults = {}
    for c in products_table.columns:
        if c.server_default is not None:
            if isinstance(c.type, String):
                server_defaults[c.name] = c.server_default.arg
            elif isinstance(c.type, postgresql.JSONB):
                m = re.match(r"^'(.+)'::jsonb$", c.server_default.arg.text)
                if m:
                    server_defaults[c.name] = json.loads(m.group(1))
    return server_defaults


@pytest.fixture
def fake_product_from_db(
    faker: Faker, product_name: ProductName, product_db_server_defaults: dict[str, Any]
) -> dict[str, Any]:
    return random_product(
        name=product_name,
        fake=faker,
        **product_db_server_defaults,
    )
