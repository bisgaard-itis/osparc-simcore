# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-variable


import json

import pytest
from aiohttp.test_utils import TestClient
from faker import Faker
from pytest import MonkeyPatch
from pytest_simcore.helpers.utils_envs import EnvVarsDict, setenvs_from_dict
from pytest_simcore.helpers.utils_login import NewUser, UserInfoDict
from simcore_service_webserver.login.settings import LoginOptions, get_plugin_options
from simcore_service_webserver.login.storage import AsyncpgStorage, get_plugin_storage


@pytest.fixture
def app_environment(app_environment: EnvVarsDict, monkeypatch: MonkeyPatch):
    envs_plugins = setenvs_from_dict(
        monkeypatch,
        {
            "WEBSERVER_ACTIVITY": "null",
            "WEBSERVER_CLUSTERS": "null",
            "WEBSERVER_COMPUTATION": "null",
            "WEBSERVER_DIAGNOSTICS": "null",
            "WEBSERVER_DIRECTOR": "null",
            "WEBSERVER_EXPORTER": "null",
            "WEBSERVER_GARBAGE_COLLECTOR": "null",
            "WEBSERVER_GROUPS": "1",
            "WEBSERVER_META_MODELING": "null",
            "WEBSERVER_PRODUCTS": "1",
            "WEBSERVER_PUBLICATIONS": "0",
            "WEBSERVER_REMOTE_DEBUG": "0",
            "WEBSERVER_SOCKETIO": "1",  # for login notifications
            "WEBSERVER_STUDIES_ACCESS_ENABLED": "0",
            "WEBSERVER_TAGS": "1",
            "WEBSERVER_TRACING": "null",
            "WEBSERVER_USERS": "1",
            "WEBSERVER_VERSION_CONTROL": "0",
        },
    )

    monkeypatch.delenv("WEBSERVER_LOGIN", raising=False)
    app_environment.pop("WEBSERVER_LOGIN", None)

    envs_login = setenvs_from_dict(
        monkeypatch,
        {
            "LOGIN_REGISTRATION_CONFIRMATION_REQUIRED": "1",
            "LOGIN_REGISTRATION_INVITATION_REQUIRED": "1",
            "LOGIN_2FA_CODE_EXPIRATION_SEC": "60",
        },
    )

    monkeypatch.delenv("LOGIN_TWILIO", raising=False)
    app_environment.pop("LOGIN_TWILIO", None)

    envs_twilio = setenvs_from_dict(
        monkeypatch,
        {
            "TWILIO_ACCOUNT_SID": "fake-twilio-account",
            "TWILIO_AUTH_TOKEN": "fake-twilio-token",
            "TWILIO_COUNTRY_CODES_W_ALPHANUMERIC_SID_SUPPORT": json.dumps(["41"]),
        },
    )

    return {**app_environment, **envs_plugins, **envs_login, **envs_twilio}


@pytest.fixture
def fake_user_email(faker: Faker) -> str:
    return faker.email()


@pytest.fixture
def fake_user_name(fake_user_email: str) -> str:
    return fake_user_email.split("@")[0]


@pytest.fixture
def fake_user_phone_number(faker: Faker) -> str:
    return faker.phone_number()


@pytest.fixture
def fake_user_password(faker: Faker) -> str:
    return faker.password(
        length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
    )


@pytest.fixture
def db(client: TestClient) -> AsyncpgStorage:
    """login database repository instance"""
    assert client.app
    db: AsyncpgStorage = get_plugin_storage(client.app)
    assert db
    return db


@pytest.fixture
def login_options(client: TestClient) -> LoginOptions:
    """app's login options"""
    assert client.app
    cfg: LoginOptions = get_plugin_options(client.app)
    assert cfg
    return cfg


@pytest.fixture
async def registered_user(
    fake_user_name: str,
    fake_user_email: str,
    fake_user_password: str,
    fake_user_phone_number: str,
    client: TestClient,
) -> UserInfoDict:
    async with NewUser(
        params={
            "name": fake_user_name,
            "email": fake_user_email,
            "password": fake_user_password,
            "phone": fake_user_phone_number,
            # active user
        },
        app=client.app,
    ) as user:
        yield user
