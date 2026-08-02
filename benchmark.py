import asyncio
import time
from functools import partial

from async_batch_faker import AsyncBatchFaker


async def run_benchmark():
    print("🚀 Initializing AsyncBatchFaker...")
    # Loading the localized data we just stole
    fake = AsyncBatchFaker(locale="ur_PK")

    # A heavy schema hitting multiple data types, auto-discovered files, and numpy math
    schema = {
        "id": fake.uuid4,
        "name": fake.full_name,
        "email": fake.email,
        "city": fake.city,
        "ip_address": fake.ipv4,
        "crypto_wallet": fake.cryptocurrency_code,
        "joined_at": partial(
            fake.date_between, start_date="2020-01-01", end_date="2026-01-01"
        ),
    }

    total_records = 1_000_000
    batch_size = 100_000

    print(f"\n⚡ Benchmarking: Generating {total_records:,} complex records...")
    print(f"📦 Processing in batches of {batch_size:,} to optimize RAM...")

    # Start the timer
    start_time = time.perf_counter()

    records_generated = 0
    # We iterate through the batches, but we won't print them to the console
    # (printing 1M lines to a terminal would bottleneck the test)
    async for batch in fake.generate_batches(
        schema=schema, total=total_records, batch_size=batch_size
    ):
        records_generated += len(batch)

    # Stop the timer
    end_time = time.perf_counter()
    elapsed = end_time - start_time

    rows_per_second = records_generated / elapsed

    print("\n" + "=" * 45)
    print("🏆 BENCHMARK RESULTS")
    print("=" * 45)
    print(f"Total Records   : {records_generated:,}")
    print(f"Time Taken      : {elapsed:.3f} seconds")
    print(f"Throughput      : {rows_per_second:,.0f} rows / second")
    print("=" * 45)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
