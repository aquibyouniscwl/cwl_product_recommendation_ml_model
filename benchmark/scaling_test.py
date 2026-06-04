import random
import time
import statistics
import asyncio
import aiohttp
import psutil
import os

# =====================================================
# CONFIG
# =====================================================
API_URL = "http://127.0.0.1:8001/recommend"
PAYLOAD_MODE = "ml1"
TOP_K = 10
# =====================================================
# PRODUCT IDS
# =====================================================
PRODUCT_IDS = [
    "product_1",
    "product_2",
    "product_3",
    "product_4",
    "product_5",
    "product_6",
    "product_7",
    "product_8",
    "product_9",
    "product_10",
    "product_11",
    "product_12",
    "product_13",
    "product_14",
    "product_15",
    "product_16",
    "product_17",
    "product_18",
    "product_19",
    "product_20",
    "product_21",
    "product_22",
    "product_23",
    "product_24",
    "product_25",
    "product_26",
    "product_27",
    "product_28",
    "product_29",
]


# =====================================================
# PAYLOAD
# =====================================================
def generate_payload(top_k):
    cart_size = random.randint(1, 3)
    enrolled_size = random.randint(0, 2)
    cart_products = random.sample(PRODUCT_IDS, cart_size)
    enrolled_products = random.sample(PRODUCT_IDS, enrolled_size)
    if PAYLOAD_MODE == "ml1":
        return {
            "cartProducts": cart_products,
            "enrolledProducts": enrolled_products,
            "topK": top_k,
        }
    return {
        "cart_items": cart_products,
        "enrolled_items": enrolled_products,
        "top_k": top_k,
    }


# =====================================================
# SINGLE REQUEST
# =====================================================
async def make_request(
    session, response_times, success_counter, failure_counter, cache_hits, cache_misses
):
    payload = generate_payload(TOP_K)
    start_time = time.perf_counter()
    try:
        async with session.post(API_URL, json=payload, timeout=120) as response:
            response_json = await response.json()
            end_time = time.perf_counter()
            response_times.append(end_time - start_time)
            cache_status = response_json.get("cache_status")
            if cache_status == "hit":
                cache_hits.append(1)
            elif cache_status == "miss":
                cache_misses.append(1)
            if response.status == 200:
                success_counter.append(1)
            else:
                failure_counter.append(1)
    except Exception:
        failure_counter.append(1)


# =====================================================
# MEMORY MONITOR
# =====================================================
async def monitor_memory(memory_snapshots):
    process = psutil.Process(os.getpid())
    while True:
        memory_mb = process.memory_info().rss / 1024 / 1024
        memory_snapshots.append(memory_mb)
        await asyncio.sleep(1)


# =====================================================
# TEST
# =====================================================
async def run_scalability_test(total_users, concurrent_users):
    response_times = []
    success_counter = []
    failure_counter = []
    cache_hits = []
    cache_misses = []
    memory_snapshots = []
    overall_start = time.perf_counter()
    memory_task = asyncio.create_task(monitor_memory(memory_snapshots))
    connector = aiohttp.TCPConnector(limit=concurrent_users)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            asyncio.create_task(
                make_request(
                    session,
                    response_times,
                    success_counter,
                    failure_counter,
                    cache_hits,
                    cache_misses,
                )
            )
            for _ in range(total_users)
        ]
        await asyncio.gather(*tasks)
    memory_task.cancel()
    overall_end = time.perf_counter()
    total_duration = overall_end - overall_start
    avg_response = statistics.mean(response_times) if response_times else 0
    median_response = statistics.median(response_times) if response_times else 0
    min_response = min(response_times) if response_times else 0
    max_response = max(response_times) if response_times else 0
    requests_per_second = (
        len(success_counter) / total_duration if total_duration > 0 else 0
    )
    avg_memory = statistics.mean(memory_snapshots) if memory_snapshots else 0
    peak_memory = max(memory_snapshots) if memory_snapshots else 0
    total_cache_requests = len(cache_hits) + len(cache_misses)
    cache_hit_ratio = (
        (len(cache_hits) / total_cache_requests) * 100
        if total_cache_requests > 0
        else 0
    )
    return {
        "total_requests": total_users,
        "successful_requests": len(success_counter),
        "failed_requests": len(failure_counter),
        "cache_hits": len(cache_hits),
        "cache_misses": len(cache_misses),
        "cache_hit_ratio_percent": round(cache_hit_ratio, 2),
        "total_test_time_seconds": round(total_duration, 4),
        "requests_per_second": round(requests_per_second, 2),
        "average_response_time_seconds": round(avg_response, 4),
        "median_response_time_seconds": round(median_response, 4),
        "minimum_response_time_seconds": round(min_response, 4),
        "maximum_response_time_seconds": round(max_response, 4),
        "average_memory_usage_mb": round(avg_memory, 2),
        "peak_memory_usage_mb": round(peak_memory, 2),
    }
