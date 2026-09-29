from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError


class ReadinessService:
    def __init__(self, postgres, redis) -> None:
        self.postgres = postgres
        self.redis = redis

    async def failed_dependency(self) -> str | None:
        try:
            await self.postgres.check()
        except SQLAlchemyError:
            return "postgres"
        try:
            await self.redis.check()
        except RedisError:
            return "redis"
        return None
