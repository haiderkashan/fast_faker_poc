import time
import tracemalloc
import platform
import sys
import matplotlib.pyplot as plt
from faker import Faker
from async_batch_faker import AsyncBatchFaker

# ---------------------------------------------------------
# 1. GENERATOR FUNCTIONS (Apples-to-Apples Schema)
# ---------------------------------------------------------
def generate_standard_faker(size):
    faker = Faker("en_US")
    data = []
    for _ in range(size):
        data.append({
            "id": faker.uuid4(),
            "name": faker.name(),
            "email": faker.email(),
        })
    return data

def generate_async_batch_faker(size):
    fake = AsyncBatchFaker(locale="en_US")
    schema = {
        "id": fake.uuid4,
        "name": fake.full_name,
        "email": fake.email,
    }
    return fake.generate(schema, total=size)

# ---------------------------------------------------------
# 2. BENCHMARK RUNNER (Time & Memory Profiling)
# ---------------------------------------------------------
def run_comparison():
    sizes = [10_000, 50_000, 100_000]
    results = []

    print("\n🚀 Starting Benchmarks (This may take a minute for standard Faker)...\n")

    for size in sizes:
        print(f"Testing {size:,} rows...")
        
        # Test Standard Faker
        tracemalloc.start()
        start = time.perf_counter()
        generate_standard_faker(size)
        faker_time = time.perf_counter() - start
        _, faker_peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Test Async Batch Faker
        tracemalloc.start()
        start = time.perf_counter()
        generate_async_batch_faker(size)
        async_time = time.perf_counter() - start
        _, async_peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        speedup = faker_time / async_time if async_time > 0 else 0
        
        results.append({
            "size": size,
            "faker_time": faker_time,
            "async_time": async_time,
            "speedup": speedup,
            "faker_mem_mb": faker_peak_mem / (1024 * 1024),
            "async_mem_mb": async_peak_mem / (1024 * 1024)
        })

    return results

# ---------------------------------------------------------
# 3 & 4. OUTPUT FORMATTER & CHART GENERATOR
# ---------------------------------------------------------
def print_markdown_table(results):
    print("\n### Benchmark Results")
    print("| Rows | Standard Faker Time | async-batch-faker Time | Speedup | Standard RAM | Async RAM |")
    print("|---|---|---|---|---|---|")
    for r in results:
        print(f"| {r['size']:,} | {r['faker_time']:.2f}s | **{r['async_time']:.4f}s** | **{r['speedup']:.1f}x Faster** | {r['faker_mem_mb']:.1f} MB | {r['async_mem_mb']:.1f} MB |")
    
    # Print Environment Specs
    print(f"\n*Benchmark Environment: {platform.system()} {platform.release()} ({platform.machine()}), Python {sys.version.split()[0]}*")

def generate_chart(results):
    sizes = [str(r["size"]) for r in results]
    faker_times = [r["faker_time"] for r in results]
    async_times = [r["async_time"] for r in results]

    x = range(len(sizes))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([i - width/2 for i in x], faker_times, width, label='Standard Faker', color='#ff6b6b')
    ax.bar([i + width/2 for i in x], async_times, width, label='Async Batch Faker', color='#4ecdc4')

    ax.set_ylabel('Execution Time (Seconds)')
    ax.set_title('Performance Comparison (Lower is Better)')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s} Rows" for s in sizes])
    ax.legend()

    plt.tight_layout()
    chart_path = "benchmark_chart.png"
    plt.savefig(chart_path, dpi=300)
    print(f"\n📊 Chart saved successfully to: {chart_path}")

if __name__ == "__main__":
    benchmark_results = run_comparison()
    print_markdown_table(benchmark_results)
    generate_chart(benchmark_results)