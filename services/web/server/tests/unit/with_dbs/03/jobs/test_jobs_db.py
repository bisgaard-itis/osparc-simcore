from aiohttp.test_utils import TestClient
from faker import Faker
from simcore_service_webserver.projects.models import ProjectDict


async def test_create_job(user_project: ProjectDict, client: TestClient, faker: Faker):
    assert client.app
    client.app.router
