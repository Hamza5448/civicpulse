from app.providers.cache.redis import RedisStatsCache
from app.repositories.complaints import ComplaintRepository


class StatsService:
    cache_key = "stats:complaints"

    def __init__(self, repository: ComplaintRepository, cache: RedisStatsCache, ttl_seconds: int) -> None:
        self.repository = repository
        self.cache = cache
        self.ttl_seconds = ttl_seconds

    async def get(self) -> tuple[dict, bool]:
        cached = await self.cache.get(self.cache_key)
        if cached is not None:
            return cached, True
        value = await self.repository.stats()
        await self.cache.set(self.cache_key, value, self.ttl_seconds)
        return value, False

    async def invalidate(self) -> None:
        await self.cache.delete(self.cache_key)
