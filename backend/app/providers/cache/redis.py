import json
from typing import Protocol


class StatsCache(Protocol):
    async def get(self, key: str) -> dict | None: ...

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None: ...

    async def delete(self, key: str) -> None: ...


class RedisStatsCache:
    def __init__(self, redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> dict | None:
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        await self.redis.set(key, json.dumps(value), ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_stats(self) -> None:
        await self.delete("stats:complaints")


class RedisJsonCache:
    def __init__(self, redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> dict | None:
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        await self.redis.set(key, json.dumps(value), ex=ttl_seconds)


class RedisRateLimiter:
    def __init__(self, redis, limit: int, window_seconds: int) -> None:
        self.redis = redis
        self.limit = limit
        self.window_seconds = window_seconds

    async def check(self, client_key: str) -> tuple[bool, int]:
        key = f"rate:complaints:{client_key}"
        async with self.redis.pipeline(transaction=True) as pipeline:
            pipeline.incr(key)
            pipeline.ttl(key)
            count, ttl = await pipeline.execute()
        if count == 1:
            await self.redis.expire(key, self.window_seconds)
            ttl = self.window_seconds
        return count <= self.limit, max(1, ttl)
