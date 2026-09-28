import pytest
from fakeredis.aioredis import FakeRedis

from app.providers.cache.redis import RedisRateLimiter, RedisStatsCache


@pytest.mark.asyncio
async def test_stats_cache_round_trip_and_expiration() -> None:
    redis = FakeRedis(decode_responses=True)
    cache = RedisStatsCache(redis)
    await cache.set("stats:test", {"count": 3}, ttl_seconds=30)
    assert await cache.get("stats:test") == {"count": 3}
    await cache.delete("stats:test")
    assert await cache.get("stats:test") is None
    await redis.aclose()


@pytest.mark.asyncio
async def test_rate_limiter_counts_per_client() -> None:
    redis = FakeRedis(decode_responses=True)
    limiter = RedisRateLimiter(redis, limit=1, window_seconds=60)
    assert (await limiter.check("client-a"))[0] is True
    assert (await limiter.check("client-a"))[0] is False
    assert (await limiter.check("client-b"))[0] is True
    await redis.aclose()