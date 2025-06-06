# pylint: disable=inconsistent-return-statements
# pylint: disable=redefined-outer-name

from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from faker import Faker
from pytest_simcore.helpers.faker_factories import random_user
from simcore_postgres_database.models.users import UserRole, users
from simcore_postgres_database.utils_user_preferences import (
    BasePreferencesRepo,
    FrontendUserPreferencesRepo,
    UserServicesUserPreferencesRepo,
)
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.fixture
def preference_one() -> str:
    return "pref_one"


@pytest.fixture
def preference_two() -> str:
    return "pref_two"


@pytest.fixture
async def product_name(
    create_fake_product: Callable[[str], Awaitable[Row]],
) -> str:
    product = await create_fake_product("fake-product")
    return product[0]


@pytest.fixture(params=[FrontendUserPreferencesRepo, UserServicesUserPreferencesRepo])
def preference_repo(request: pytest.FixtureRequest) -> type[BasePreferencesRepo]:
    return request.param


async def _assert_save_get_preference(
    asyncpg_engine: AsyncEngine,
    preference_repo: type[BasePreferencesRepo],
    *,
    user_id: int,
    preference_name: str,
    product_name: str,
    payload: Any,
) -> None:
    async with asyncpg_engine.begin() as connection:
        await preference_repo.save(
            connection,
            user_id=user_id,
            preference_name=preference_name,
            product_name=product_name,
            payload=payload,
        )
    async with asyncpg_engine.connect() as connection:
        get_res_2: Any | None = await preference_repo.load(
            connection,
            user_id=user_id,
            preference_name=preference_name,
            product_name=product_name,
        )
    assert get_res_2 is not None
    assert get_res_2 == payload


async def _assert_preference_not_saved(
    asyncpg_engine: AsyncEngine,
    preference_repo: type[BasePreferencesRepo],
    *,
    user_id: int,
    preference_name: str,
    product_name: str,
) -> None:
    async with asyncpg_engine.connect() as connection:
        not_found: Any | None = await preference_repo.load(
            connection,
            user_id=user_id,
            preference_name=preference_name,
            product_name=product_name,
        )
    assert not_found is None


def _get_random_payload(
    faker: Faker, preference_repo: type[BasePreferencesRepo]
) -> Any:
    if preference_repo == FrontendUserPreferencesRepo:
        return {faker.pystr(): faker.pystr()}
    if preference_repo == UserServicesUserPreferencesRepo:
        return faker.pystr(max_chars=10000).encode()

    pytest.fail(f"Did not define a casa for {preference_repo=}. Please add one.")


async def _create_user_id(asyncpg_engine: AsyncEngine, faker: Faker) -> int:
    data = random_user(role=faker.random_element(elements=UserRole))
    async with asyncpg_engine.begin() as connection:
        user_id = await connection.scalar(
            users.insert().values(**data).returning(users.c.id)
        )
    assert user_id
    return user_id


async def test_user_preference_repo_workflow(
    asyncpg_engine: AsyncEngine,
    preference_repo: type[BasePreferencesRepo],
    preference_one: str,
    product_name: str,
    faker: Faker,
):
    user_id = await _create_user_id(asyncpg_engine, faker)
    # preference is not saved
    await _assert_preference_not_saved(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_name,
    )

    payload_1 = _get_random_payload(faker, preference_repo)
    payload_2 = _get_random_payload(faker, preference_repo)
    assert payload_1 != payload_2

    # store the preference for the first time
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_name,
        payload=payload_1,
    )

    # updating the preference still works
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_name,
        payload=payload_2,
    )


async def test__same_preference_name_product_name__different_users(
    asyncpg_engine: AsyncEngine,
    preference_repo: type[BasePreferencesRepo],
    preference_one: str,
    product_name: str,
    faker: Faker,
):
    user_id_1 = await _create_user_id(asyncpg_engine, faker)
    user_id_2 = await _create_user_id(asyncpg_engine, faker)

    payload_1 = _get_random_payload(faker, preference_repo)
    payload_2 = _get_random_payload(faker, preference_repo)
    assert payload_1 != payload_2

    # save preference for first user
    await _assert_preference_not_saved(
        asyncpg_engine,
        preference_repo,
        user_id=user_id_1,
        preference_name=preference_one,
        product_name=product_name,
    )
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id_1,
        preference_name=preference_one,
        product_name=product_name,
        payload=payload_1,
    )

    # save preference for second user
    await _assert_preference_not_saved(
        asyncpg_engine,
        preference_repo,
        user_id=user_id_2,
        preference_name=preference_one,
        product_name=product_name,
    )
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id_2,
        preference_name=preference_one,
        product_name=product_name,
        payload=payload_2,
    )


async def test__same_user_preference_name__different_product_name(
    asyncpg_engine: AsyncEngine,
    create_fake_product: Callable[[str], Awaitable[Row]],
    preference_repo: type[BasePreferencesRepo],
    preference_one: str,
    faker: Faker,
):
    product_1 = (await create_fake_product("fake-product-1"))[0]
    product_2 = (await create_fake_product("fake-product-2"))[0]

    user_id = await _create_user_id(asyncpg_engine, faker)

    payload_1 = _get_random_payload(faker, preference_repo)
    payload_2 = _get_random_payload(faker, preference_repo)
    assert payload_1 != payload_2

    # save for first product_name
    await _assert_preference_not_saved(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_1,
    )
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_1,
        payload=payload_1,
    )

    # save for second product_name
    await _assert_preference_not_saved(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_2,
    )
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_2,
        payload=payload_2,
    )


async def test__same_product_name_user__different_preference_name(
    asyncpg_engine: AsyncEngine,
    preference_repo: type[BasePreferencesRepo],
    preference_one: str,
    preference_two: str,
    product_name: str,
    faker: Faker,
):
    user_id = await _create_user_id(asyncpg_engine, faker)

    payload_1 = _get_random_payload(faker, preference_repo)
    payload_2 = _get_random_payload(faker, preference_repo)
    assert payload_1 != payload_2

    # save first preference
    await _assert_preference_not_saved(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_name,
    )
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_one,
        product_name=product_name,
        payload=payload_1,
    )

    # save second preference
    await _assert_preference_not_saved(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_two,
        product_name=product_name,
    )
    await _assert_save_get_preference(
        asyncpg_engine,
        preference_repo,
        user_id=user_id,
        preference_name=preference_two,
        product_name=product_name,
        payload=payload_2,
    )
