import asyncio
import subprocess
import time
import pandas as pd
from scaling_test import run_scalability_test

# =====================================================
# BENCHMARK CONFIGURATION
# =====================================================

# [1]
# USER_LEVELS = [1000, 5000, 10000]
# CONCURRENT_LEVELS = [100, 300]
# WORKER_LEVELS = [1, 2, 4]
# OUTPUT_FILE = "benchmark_results.xlsx"

# [2]
# USER_LEVELS = [1000, 5000, 10000]
# CONCURRENT_LEVELS = [500]
# WORKER_LEVELS = [2]
# OUTPUT_FILE = "benchmark_results2.xlsx"

# [3]
USER_LEVELS = [10000, 20000]
CONCURRENT_LEVELS = [2000]
WORKER_LEVELS = [2, 4]
OUTPUT_FILE = "benchmark_results/benchmark_results3.xlsx"

# =====================================================
# START UVICORN SERVER
# =====================================================

def start_server(workers):
    command = ["uvicorn", "src.api.app:app", "--workers", str(workers)]
    process = subprocess.Popen(command)
    print(f"\nStarting server with {workers} workers...\n")
    time.sleep(10)
    return process

# =====================================================
# STOP UVICORN SERVER
# =====================================================

def stop_server(process):
    process.terminate()
    process.wait()
    print("\nServer stopped.\n")

# =====================================================
# RUN ALL BENCHMARKS
# =====================================================

async def run_all_benchmarks():
    benchmark_results = []
    total_runs = len(USER_LEVELS) * len(CONCURRENT_LEVELS) * len(WORKER_LEVELS)
    current_run = 1
    for workers in WORKER_LEVELS:
        server_process = start_server(workers)
        for users in USER_LEVELS:
            for concurrency in CONCURRENT_LEVELS:
                print("\n====================================")
                print(f"RUN {current_run}/{total_runs}")
                print("====================================")
                print(f"Users: {users}")
                print(f"Concurrent: {concurrency}")
                print(f"Workers: {workers}")
                print("\nRunning benchmark...\n")
                result = await run_scalability_test(total_users=users, concurrent_users=concurrency)
                result["workers"] = workers
                result["concurrent_users"] = concurrency
                benchmark_results.append(result)
                dataframe = pd.DataFrame(benchmark_results)
                dataframe.to_excel(OUTPUT_FILE, index=False)
                print("\nBenchmark complete.\n")
                print(result)
                current_run += 1
        stop_server(server_process)
    print("\n====================================")
    print("ALL BENCHMARKS COMPLETED")
    print("====================================")
    print(f"\nResults saved to: {OUTPUT_FILE}\n")

# =====================================================
# ENTRYPOINT
# =====================================================

if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())