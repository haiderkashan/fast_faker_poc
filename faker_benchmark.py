import time

from faker import Faker


def run_standard_benchmark():
    print("🚀 Initializing Standard Faker...")
    fake = Faker("en_PK")
    total_records = 100_000  # Testing 10% of your engine's volume

    print(f"\n🐢 Benchmarking: Generating {total_records:,} records one-by-one...")

    start_time = time.perf_counter()
    records = []

    # Standard Faker requires slow Python loops
    for _ in range(total_records):
        records.append(
            {
                "id": fake.uuid4(),
                "name": fake.name(),
                "email": fake.email(),
                "city": fake.city(),
                "ip_address": fake.ipv4(),
            }
        )

    end_time = time.perf_counter()
    elapsed = end_time - start_time
    rows_per_second = total_records / elapsed

    print("\n" + "=" * 45)
    print("🐢 STANDARD FAKER RESULTS")
    print("=" * 45)
    print(f"Total Records   : {total_records:,}")
    print(f"Time Taken      : {elapsed:.3f} seconds")
    print(f"Throughput      : {rows_per_second:,.0f} rows / second")
    print(f"Estimated 1M    : {(elapsed * 10):.0f} seconds")
    print("=" * 45)


if __name__ == "__main__":
    run_standard_benchmark()
