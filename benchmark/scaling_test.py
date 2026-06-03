import random
import time
import statistics
import asyncio
import aiohttp
import psutil
import os

# =====================================================
# SAMPLE PRODUCT IDS
# =====================================================

PRODUCT_IDS = [
    "mcrta", "grts", "awrts", "azrts", "hmcrts", "rts", "rta", "arta", "adrts",
    "lms", "drta", "rtid", "csa", "cse", "opo", "btf", "cda", "pta", "ptf",
    "k8srta", "ocwai", "pia", "scas", "sco", "edp", "wirto"
]

# =====================================================
# GENERATE RANDOM PAYLOAD
# =====================================================

def generate_random_payload(top_k):
    cart_size = random.randint(1, 3)
    enrolled_size = random.randint(0, 2)
    cart_products = random.sample(PRODUCT_IDS, cart_size)
    enrolled_products = random.sample(PRODUCT_IDS, enrolled_size)
    return {"cartProducts": cart_products, "enrolledProducts": enrolled_products, "topK": top_k}

# =====================================================
# SINGLE REQUEST
# =====================================================

async def make_request(session, api_url, top_k, response_times, success_counter, failure_counter):
    payload = generate_random_payload(top_k)
    start_time = time.perf_counter()
    try:
        async with session.post(api_url, json=payload, timeout=120) as response:
            await response.json()
            end_time = time.perf_counter()
            response_times.append(end_time - start_time)
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
# RUN SCALABILITY TEST
# =====================================================

async def run_scalability_test(total_users, concurrent_users, top_k=10, api_url="http://127.0.0.1:8000/recommend"):
    response_times = []
    success_counter = []
    failure_counter = []
    memory_snapshots = []
    overall_start = time.perf_counter()
    memory_task = asyncio.create_task(monitor_memory(memory_snapshots))
    connector = aiohttp.TCPConnector(limit=concurrent_users)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(make_request(session, api_url, top_k, response_times, success_counter, failure_counter)) for _ in range(total_users)]
        await asyncio.gather(*tasks)
    memory_task.cancel()
    overall_end = time.perf_counter()
    total_duration = overall_end - overall_start
    avg_response = statistics.mean(response_times) if response_times else 0
    median_response = statistics.median(response_times) if response_times else 0
    min_response = min(response_times) if response_times else 0
    max_response = max(response_times) if response_times else 0
    requests_per_second = len(success_counter) / total_duration if total_duration > 0 else 0
    avg_memory = statistics.mean(memory_snapshots) if memory_snapshots else 0
    peak_memory = max(memory_snapshots) if memory_snapshots else 0
    return {
        "total_requests": total_users,
        "successful_requests": len(success_counter),
        "failed_requests": len(failure_counter),
        "total_test_time_seconds": round(total_duration, 4),
        "requests_per_second": round(requests_per_second, 2),
        "average_response_time_seconds": round(avg_response, 4),
        "median_response_time_seconds": round(median_response, 4),
        "minimum_response_time_seconds": round(min_response, 4),
        "maximum_response_time_seconds": round(max_response, 4),
        "average_memory_usage_mb": round(avg_memory, 2),
        "peak_memory_usage_mb": round(peak_memory, 2)
    }