# pylint: disable=all


import importlib
import random
import string
from collections.abc import Callable, Iterator
from typing import Any

import pip
import pytest
from fastapi import FastAPI
from pydantic import ValidationError
from servicelib.fastapi.tracing import (
    get_tracing_instrumentation_lifespan,
)
from settings_library.tracing import TracingSettings


@pytest.fixture
def mocked_app() -> FastAPI:
    return FastAPI(title="opentelemetry example")


@pytest.fixture
def tracing_settings_in(request: pytest.FixtureRequest) -> dict[str, Any]:
    return request.param


@pytest.fixture()
def set_and_clean_settings_env_vars(
    monkeypatch: pytest.MonkeyPatch, tracing_settings_in: Callable[[], dict[str, Any]]
) -> None:
    endpoint_mocked = False
    if tracing_settings_in[0]:
        endpoint_mocked = True
        monkeypatch.setenv(
            "TRACING_OPENTELEMETRY_COLLECTOR_ENDPOINT", f"{tracing_settings_in[0]}"
        )
    port_mocked = False
    if tracing_settings_in[1]:
        port_mocked = True
        monkeypatch.setenv(
            "TRACING_OPENTELEMETRY_COLLECTOR_PORT", f"{tracing_settings_in[1]}"
        )
    yield
    if endpoint_mocked:
        monkeypatch.delenv("TRACING_OPENTELEMETRY_COLLECTOR_ENDPOINT")
    if port_mocked:
        monkeypatch.delenv("TRACING_OPENTELEMETRY_COLLECTOR_PORT")


@pytest.mark.parametrize(
    "tracing_settings_in",
    [
        ("http://opentelemetry-collector", 4318),
        ("http://opentelemetry-collector", "4318"),
    ],
    indirect=True,
)
async def test_valid_tracing_settings(
    mocked_app: FastAPI,
    set_and_clean_settings_env_vars: Callable[[], None],
    tracing_settings_in: Callable[[], dict[str, Any]],
    uninstrument_opentelemetry: Iterator[None],
):
    tracing_settings = TracingSettings()
    async for _ in get_tracing_instrumentation_lifespan(
        tracing_settings=tracing_settings,
        service_name="Mock-Openetlemetry-Pytest",
    )(app=mocked_app):
        async for _ in get_tracing_instrumentation_lifespan(
            tracing_settings=tracing_settings,
            service_name="Mock-Openetlemetry-Pytest",
        )(app=mocked_app):
            pass


@pytest.mark.parametrize(
    "tracing_settings_in",
    [
        ("http://opentelemetry-collector", 80),
        ("http://opentelemetry-collector", 1238712936),
        ("opentelemetry-collector", 4318),
        ("httsdasp://ot@##el-collector", 4318),
        (" !@#$%^&*()[]{};:,<>?\\|`~+=/'\"", 4318),
        # The following exceeds max DNS name length
        (
            "".join(random.choice(string.ascii_letters) for _ in range(300)),
            "1238712936",
        ),  # noqa: S311
    ],
    indirect=True,
)
async def test_invalid_tracing_settings(
    mocked_app: FastAPI,
    set_and_clean_settings_env_vars: Callable[[], None],
    tracing_settings_in: Callable[[], dict[str, Any]],
    uninstrument_opentelemetry: Iterator[None],
):
    app = mocked_app
    with pytest.raises((BaseException, ValidationError, TypeError)):  # noqa: PT012
        tracing_settings = TracingSettings()
        async for _ in get_tracing_instrumentation_lifespan(
            tracing_settings=tracing_settings,
            service_name="Mock-Openetlemetry-Pytest",
        )(app=app):
            pass


def install_package(package):
    pip.main(["install", package])


def uninstall_package(package):
    pip.main(["uninstall", "-y", package])


@pytest.fixture(scope="function")
def manage_package(request):
    package, importname = request.param
    install_package(package)
    yield importname
    uninstall_package(package)


@pytest.mark.skip(
    reason="this test installs always the latest version of the package which creates conflicts."
)
@pytest.mark.parametrize(
    "tracing_settings_in, manage_package",
    [
        (
            ("http://opentelemetry-collector", 4318),
            (
                "opentelemetry-instrumentation-botocore",
                "opentelemetry.instrumentation.botocore",
            ),
        ),
        (
            ("http://opentelemetry-collector", "4318"),
            (
                "opentelemetry-instrumentation-aiopg",
                "opentelemetry.instrumentation.aiopg",
            ),
        ),
    ],
    indirect=True,
)
async def test_tracing_setup_package_detection(
    mocked_app: FastAPI,
    set_and_clean_settings_env_vars: Callable[[], None],
    tracing_settings_in: Callable[[], dict[str, Any]],
    uninstrument_opentelemetry: Iterator[None],
    manage_package,
):
    package_name = manage_package
    importlib.import_module(package_name)
    tracing_settings = TracingSettings()
    async for _ in get_tracing_instrumentation_lifespan(
        tracing_settings=tracing_settings,
        service_name="Mock-Openetlemetry-Pytest",
    )(app=mocked_app):
        # idempotency check
        async for _ in get_tracing_instrumentation_lifespan(
            tracing_settings=tracing_settings,
            service_name="Mock-Openetlemetry-Pytest",
        )(app=mocked_app):
            pass
