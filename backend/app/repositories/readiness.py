from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class PostgresReadinessRepository:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    async def check(self) -> None:
        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
