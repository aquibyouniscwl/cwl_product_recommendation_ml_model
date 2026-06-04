from src.cache.redis_client import redis_client

CACHE_ENABLED = True


def get_cache(cache_key):
    if not CACHE_ENABLED:
        print("\nCACHE DISABLED")
        return None
    if not redis_client:
        return None
    try:
        return redis_client.get(cache_key)
    except Exception:
        return None


def set_cache(cache_key, value, ttl=3600):
    if not CACHE_ENABLED:
        return
    if not redis_client:
        return
    try:
        redis_client.set(cache_key, value, ex=ttl)
    except Exception:
        pass
