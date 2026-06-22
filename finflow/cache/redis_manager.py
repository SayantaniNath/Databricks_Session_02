"""
Redis caching layer for FinFlow.
Stores latest prices and daily summaries with appropriate TTLs.

Run standalone to test:
    source ~/myenv/bin/activate
    brew services start redis
    cd ~/finflow
    python -m cache.redis_manager
"""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("redis_manager")


def get_client():
    import redis
    return redis.Redis(
        host=config.redis.host,
        port=config.redis.port,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )


def cache_price(record: dict):
    """
    Store latest price as a Redis Hash.
    Key: finflow:price:BITCOIN
    TTL: 60 seconds — stale prices are dangerous
    """
    r = get_client()
    key = f"finflow:price:{record['symbol']}"
    r.hset(key, mapping={
        "price_usd": str(record.get("price_usd", "")),
        "change_24h_pct": str(record.get("change_24h_pct", "")),
        "volume_24h_usd": str(record.get("volume_24h_usd", "")),
        "ingested_at": record.get("ingested_at", ""),
        "source": record.get("source", ""),
    })
    r.expire(key, config.redis.price_ttl_seconds)
    log.debug(f"Cached price for {record['symbol']} (TTL={config.redis.price_ttl_seconds}s)")


def get_price(symbol: str) -> dict | None:
    """
    Read from cache first.
    Returns None if cache miss — caller should fall back to Snowflake.
    """
    r = get_client()
    key = f"finflow:price:{symbol.upper()}"
    data = r.hgetall(key)
    if not data:
        log.debug(f"Cache MISS for {symbol}")
        return None
    log.debug(f"Cache HIT for {symbol}")
    return data


def cache_top_movers(movers: list):
    """
    Store top 5 movers as sorted set.
    Score = 24h change percentage.
    Key: finflow:top_movers
    """
    r = get_client()
    key = "finflow:top_movers"
    r.delete(key)
    for item in movers:
        r.zadd(key, {item["symbol"]: float(item.get("change_24h_pct") or 0)})
    r.expire(key, config.redis.price_ttl_seconds)
    log.info(f"Cached top movers: {[m['symbol'] for m in movers]}")


def get_top_movers(count: int = 5) -> list:
    """Return top N movers sorted by 24h change descending."""
    r = get_client()
    return r.zrevrange("finflow:top_movers", 0, count - 1, withscores=True)


def cache_all_prices(records: list):
    """Bulk cache all prices from a batch — used by Airflow DAG."""
    for record in records:
        try:
            cache_price(record)
        except Exception as e:
            log.error(f"Failed to cache {record.get('symbol')}: {e}")
    # Also update top movers sorted set
    valid = [r for r in records if r.get("change_24h_pct") is not None]
    if valid:
        cache_top_movers(valid)


def health_check() -> bool:
    """Verify Redis is reachable — used by Airflow sensor."""
    try:
        r = get_client()
        r.ping()
        log.info("Redis health check: OK")
        return True
    except Exception as e:
        log.error(f"Redis health check FAILED: {e}")
        return False


if __name__ == "__main__":
    if not health_check():
        print("Redis not running. Start with: brew services start redis")
        sys.exit(1)

    # Demo: cache some fake prices and read them back
    test_records = [
        {"symbol": "BITCOIN", "price_usd": 65000.0, "change_24h_pct": 2.5,
         "volume_24h_usd": 28000000000, "ingested_at": "2026-05-14T10:00:00Z", "source": "test"},
        {"symbol": "ETHEREUM", "price_usd": 3200.0, "change_24h_pct": -1.2,
         "volume_24h_usd": 15000000000, "ingested_at": "2026-05-14T10:00:00Z", "source": "test"},
    ]
    cache_all_prices(test_records)
    print("\nCached prices:")
    for r in test_records:
        cached = get_price(r["symbol"])
        print(f"  {r['symbol']}: ${cached['price_usd']}")

    print("\nTop movers:")
    for symbol, score in get_top_movers():
        print(f"  {symbol}: {score:+.2f}%")
