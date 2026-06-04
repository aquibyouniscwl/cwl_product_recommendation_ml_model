import asyncio
import subprocess
import time
import os

import pandas as pd
import redis

from scaling_test import run_scalability_test

# =====================================================
# CONFIG
# =====================================================
USER_LEVELS = [1000, 5000, 10000]
CONCURRENT_LEVELS = [300, 600]
WORKER_LEVELS = [1, 2, 4]

OUTPUT_FILE = "benchmark/after_cache_memory_update/yes_cache1.xlsx"
UVICORN_APP = "src.api.app:app"

# =====================================================
# REDIS
# =====================================================
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# =====================================================
# CLEAR CACHE
# =====================================================
def clear_redis_cache():
    try:
        redis_client.flushall()
        print("\nRedis cache cleared.\n")
    except Exception as e:
        print(f"\nRedis clear failed: {str(e)}\n")


# =====================================================
# START SERVER
# =====================================================
def start_server(workers):

    command = [
        "uvicorn",
        UVICORN_APP,
        "--port",
        "8000",
        "--workers",
        str(workers),
    ]

    process = subprocess.Popen(command)

    print(
        f"\nStarting server with "
        f"{workers} workers on port 8001...\n"
    )

    time.sleep(20)

    return process


# =====================================================
# STOP SERVER
# =====================================================
def stop_server(process):

    try:
        print("\nAttempting graceful shutdown...\n")

        process.terminate()

        process.wait(timeout=10)

    except Exception:
        pass

    try:

        if process.poll() is None:

            print(
                "\nGraceful shutdown failed. "
                "Force killing process...\n"
            )

            if os.name == "nt":
                os.system(
                    f"taskkill /F /T /PID {process.pid}"
                )
            else:
                process.kill()

    except Exception as e:

        print(
            f"\nFailed to stop process: {str(e)}\n"
        )

    print("\nServer stopped.\n")


# =====================================================
# SAVE EXCEL
# =====================================================
def save_results_to_excel(benchmark_results):

    if not benchmark_results:
        return

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    dataframe = pd.DataFrame(benchmark_results)

    ordered_columns = [

        # benchmark
        "workers",
        "concurrent_users",

        # requests
        "total_requests",
        "successful_requests",
        "failed_requests",

        # redis cache
        "cache_hits",
        "cache_misses",
        "cache_hit_ratio_percent",

        # lru cache
        "lru_hits",
        "lru_misses",
        "lru_hit_ratio_percent",

        # timing
        "total_test_time_seconds",
        "requests_per_second",

        # latency
        "average_response_time_seconds",
        "median_response_time_seconds",
        "minimum_response_time_seconds",
        "maximum_response_time_seconds",

        # memory
        "average_memory_usage_mb",
        "peak_memory_usage_mb",
    ]

    # Create missing columns if absent
    for column in ordered_columns:

        if column not in dataframe.columns:

            dataframe[column] = 0

    dataframe = dataframe[ordered_columns]

    dataframe.to_excel(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved results to "
        f"{OUTPUT_FILE}\n"
    )


# =====================================================
# RUN BENCHMARKS
# =====================================================
async def run_all_benchmarks():

    benchmark_results = []

    total_runs = (
        len(USER_LEVELS)
        * len(CONCURRENT_LEVELS)
        * len(WORKER_LEVELS)
    )

    current_run = 1

    for workers in WORKER_LEVELS:

        server_process = start_server(workers)

        try:

            for users in USER_LEVELS:

                for concurrency in CONCURRENT_LEVELS:

                    clear_redis_cache()

                    print(
                        "\n===================================="
                    )

                    print(
                        f"RUN "
                        f"{current_run}/{total_runs}"
                    )

                    print(f"Users: {users}")

                    print(
                        f"Concurrent: {concurrency}"
                    )

                    print(
                        f"Workers: {workers}"
                    )

                    result = await run_scalability_test(
                        total_users=users,
                        concurrent_users=concurrency,
                    )

                    result["workers"] = workers
                    result["concurrent_users"] = concurrency

                    benchmark_results.append(result)

                    save_results_to_excel(
                        benchmark_results
                    )

                    print("\nRESULT\n")
                    print(result)

                    current_run += 1

        finally:

            stop_server(server_process)

    print(
        f"\nResults saved to: "
        f"{OUTPUT_FILE}\n"
    )


# =====================================================
# ENTRYPOINT
# =====================================================
if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())