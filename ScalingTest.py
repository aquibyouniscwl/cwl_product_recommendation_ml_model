import random
import time
import statistics
import asyncio
import aiohttp
import psutil
import os
import json
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================

API_URL = "http://127.0.0.1:8000/recommend"
TOTAL_USERS = 1000
CONCURRENT_USERS = 100
TOP_K = 10
OUTPUT_FILE = "scalability_results.json"

# =====================================================
# SAMPLE PRODUCT IDS
# =====================================================

PRODUCT_IDS = [
    "mcrta", "grts", "awrts", "azrts", "hmcrts", "rts", "rta", "arta", "adrts",
    "lms", "drta", "rtid", "csa", "cse", "opo", "btf", "cda", "pta", "ptf",
    "k8srta", "ocwai", "pia", "scas", "sco", "edp", "wirto"
]

# =====================================================
# PERFORMANCE METRICS
# =====================================================

response_times = []
success_count = 0
failure_count = 0
memory_snapshots = []
all_request_logs = []

# =====================================================
# GENERATE RANDOM REQUEST BODY
# =====================================================

def generate_random_payload():
    cart_size = random.randint(1, 3)
    enrolled_size = random.randint(0, 2)
    cart_products = random.sample(PRODUCT_IDS, cart_size)
    enrolled_products = random.sample(PRODUCT_IDS, enrolled_size)
    return {"cartProducts": cart_products, "enrolledProducts": enrolled_products, "topK": TOP_K}

# =====================================================
# SINGLE API REQUEST
# =====================================================

async def make_request(session, user_id):
    global success_count, failure_count
    payload = generate_random_payload()
    start_time = time.perf_counter()
    request_log = {
        "user_id": user_id,
        "timestamp": str(datetime.utcnow()),
        "request": payload,
        "response": None,
        "status_code": None,
        "response_time_seconds": None,
        "success": False,
        "error": None
    }
    try:
        async with session.post(API_URL, json=payload, timeout=60) as response:
            response_json = await response.json()
            end_time = time.perf_counter()
            response_time = end_time - start_time
            response_times.append(response_time)
            request_log["response"] = response_json
            request_log["status_code"] = response.status
            request_log["response_time_seconds"] = round(response_time, 4)
            if response.status == 200:
                request_log["success"] = True
                success_count += 1
                print(f"[USER {user_id}] SUCCESS {response_time:.4f}s")
            else:
                failure_count += 1
                print(f"[USER {user_id}] FAILED STATUS={response.status}")
    except Exception as error:
        failure_count += 1
        request_log["error"] = str(error)
        print(f"[USER {user_id}] ERROR: {str(error)}")
    all_request_logs.append(request_log)

# =====================================================
# MEMORY MONITOR
# =====================================================

async def monitor_memory():
    process = psutil.Process(os.getpid())
    while True:
        memory_mb = process.memory_info().rss / 1024 / 1024
        memory_snapshots.append(memory_mb)
        await asyncio.sleep(1)

# =====================================================
# LOAD TEST
# =====================================================

async def run_load_test():
    connector = aiohttp.TCPConnector(limit=CONCURRENT_USERS)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(make_request(session, user_id + 1)) for user_id in range(TOTAL_USERS)]
        await asyncio.gather(*tasks)

# =====================================================
# SAVE RESULTS
# =====================================================

def save_results():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(all_request_logs, file, indent=2)

# =====================================================
# MAIN TEST RUNNER
# =====================================================

async def main():
    print("\n====================================")
    print("STARTING SCALABILITY TEST")
    print("====================================\n")
    overall_start = time.perf_counter()
    memory_task = asyncio.create_task(monitor_memory())
    await run_load_test()
    memory_task.cancel()
    overall_end = time.perf_counter()
    total_duration = overall_end - overall_start
    avg_response = statistics.mean(response_times) if response_times else 0
    min_response = min(response_times) if response_times else 0
    max_response = max(response_times) if response_times else 0
    median_response = statistics.median(response_times) if response_times else 0
    requests_per_second = success_count / total_duration if total_duration > 0 else 0
    avg_memory = statistics.mean(memory_snapshots) if memory_snapshots else 0
    peak_memory = max(memory_snapshots) if memory_snapshots else 0
    save_results()
    print("\n====================================")
    print("SCALABILITY TEST REPORT")
    print("====================================\n")
    print(f"Total Requests: {TOTAL_USERS}")
    print(f"Successful Requests: {success_count}")
    print(f"Failed Requests: {failure_count}")
    print(f"Total Test Time: {total_duration:.2f}s")
    print(f"Requests Per Second: {requests_per_second:.2f}")
    print("\n====================================")
    print("RESPONSE TIME METRICS")
    print("====================================\n")
    print(f"Average Response Time: {avg_response:.4f}s")
    print(f"Median Response Time: {median_response:.4f}s")
    print(f"Minimum Response Time: {min_response:.4f}s")
    print(f"Maximum Response Time: {max_response:.4f}s")
    print("\n====================================")
    print("MEMORY METRICS")
    print("====================================\n")
    print(f"Average Memory Usage: {avg_memory:.2f} MB")
    print(f"Peak Memory Usage: {peak_memory:.2f} MB")
    print("\n====================================")
    print("RESULTS SAVED")
    print("====================================\n")
    print(f"Saved all request logs to:")
    print(f"{OUTPUT_FILE}")
    print("\n====================================")
    print("TEST COMPLETED")
    print("====================================\n")

# =====================================================
# ENTRYPOINT
# =====================================================

if __name__ == "__main__":
    asyncio.run(main())