from src.cache.redis_client import redis_client

# CACHE_ENABLED = False
CACHE_ENABLED = True

# =====================================================
# CONFIG
# =====================================================
CACHE_TTL_SECONDS = 3600


# =====================================================
# GET CACHE
# =====================================================
def get_cache(cache_key):

    if not CACHE_ENABLED:

        return None

    if not redis_client:

        return None

    try:

        return redis_client.get(
            cache_key
        )

    except Exception as e:

        print(
            f"\nRedis GET Error: {e}\n"
        )

        return None


# =====================================================
# SET CACHE
# =====================================================
def set_cache(
    cache_key,
    value,
    ttl=CACHE_TTL_SECONDS,
):

    if not CACHE_ENABLED:

        return

    if not redis_client:

        return

    try:

        redis_client.set(
            cache_key,
            value,
            ex=ttl,
        )

    except Exception as e:

        print(
            f"\nRedis SET Error: {e}\n"
        )


# =====================================================
# DELETE CACHE
# =====================================================
def delete_cache(
    cache_key,
):

    if not CACHE_ENABLED:

        return

    if not redis_client:

        return

    try:

        redis_client.delete(
            cache_key
        )

    except Exception as e:

        print(
            f"\nRedis DELETE Error: {e}\n"
        )


# =====================================================
# CACHE INFO
# =====================================================
def get_cache_info():

    if not CACHE_ENABLED:

        return {}

    try:

        info = redis_client.info()

        return {
            "used_memory_mb": round(
                info.get(
                    "used_memory",
                    0,
                )
                / 1024
                / 1024,
                2,
            ),
            "evicted_keys": info.get(
                "evicted_keys",
                0,
            ),
            "connected_clients": info.get(
                "connected_clients",
                0,
            ),
            "total_keys": redis_client.dbsize(),
        }

    except Exception:

        return {}