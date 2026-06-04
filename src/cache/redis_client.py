import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

try:

    redis_client.ping()

    redis_client.config_set(
        "maxmemory",
        "500mb"
    )

    redis_client.config_set(
        "maxmemory-policy",
        "allkeys-lfu"
    )

    print(
        "\nRedis Connected"
        "\nMax Memory: 500MB"
        "\nEviction Policy: allkeys-lfu\n"
    )

except Exception as e:

    print(
        f"\nRedis initialization failed: {e}\n"
    )