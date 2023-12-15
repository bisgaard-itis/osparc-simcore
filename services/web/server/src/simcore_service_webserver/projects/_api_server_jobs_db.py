from aiopg.sa.engine import Engine
from aiopg.sa.result import ResultProxy, RowProxy
from models_library.jobs import JobRow
from simcore_postgres_database.models.projects_to_api_server_jobs import (
    projects_to_api_server_jobs,
)


async def insert_job(engine: Engine, job_row: JobRow):
    async with engine.acquire() as connection:
        async with connection.begin():
            result: ResultProxy = await connection.execute(
                projects_to_api_server_jobs.insert()
                .values(**job_row.dict())
                .returning(*[c for c in projects_to_api_server_jobs.columns])
            )
            row: RowProxy | None = await result.fetchone()
            assert row
            return JobRow.parse_obj(row.items())
