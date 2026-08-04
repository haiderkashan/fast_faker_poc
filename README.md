# ⚡ Async Batch Faker

[![PyPI version](https://badge.fury.io/py/async-batch-faker.svg)](https://badge.fury.io/py/async-batch-faker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A ridiculously fast, asynchronous, and vectorized mock data generator for Python.

Built to solve the bottleneck of seeding massive databases in modern web frameworks and data science pipelines. While standard `Faker` is great for generating a single row for unit testing, `Async Batch Faker` uses `numpy` and `asyncio` to blast hundreds of thousands of rows of localized data in seconds.

## 🚀 Performance

Benchmarked generating complex records (UUIDs, localized names, emails, IPs, crypto codes) comparing standard Python `Faker` against `Async Batch Faker` across varying scales:

### Benchmark Results

| Rows    | Faker Time | async-batch-faker Time | Speedup          | Standard RAM | Async RAM |
| ------- | ---------- | ---------------------- | ---------------- | ------------ | --------- |
| 10,000  | 34.69s     | **2.7194s**            | **12.8x Faster** | 4.9 MB       | 135.5 MB  |
| 50,000  | 175.58s    | **5.7701s**            | **30.4x Faster** | 19.7 MB      | 143.8 MB  |
| 100,000 | 348.94s    | **8.4659s**            | **41.2x Faster** | 39.2 MB      | 180.2 MB  |

_Benchmark Environment: Windows 10 (AMD64), Python 3.11.9_

## ✨ Killer Features

- **Numpy Vectorization:** Mathematical data and string concatenations are calculated instantly in C via `numpy` arrays, bypassing slow Python `for` loops.
- **Omni-Data Architecture:** Dynamically loads hundreds of localized datasets (names, cities, jobs, IPs) directly into memory from text files.
- **Typo Protection:** Built-in fuzzy matching actively suggests the correct field if you misspell a provider (e.g., typing `fake.colr` suggests `color_name`).
- **Zero-Friction DX:** Built for all skill levels. Generate simple Python lists, stream massive CSVs, or unblock your event loop with async database batching.

---

## The 100MB PyPI Bypass (Dynamic Auto-Downloading)

To bypass PyPI's strict 100MB upload limits while giving you access to gigabytes of worldwide synthetic data, this library uses a Two-Tier Architecture:

- **Lightweight Core:** The pip package installs instantly, bundling only the blazing-fast core engine and standard en_US datasets.

- **Transparent Auto-Fetching:** When you initialize an international locale (e.g., AsyncBatchFaker(locale="fr_FR")), the engine intercepts the request and silently auto-downloads the highly optimized JSON data package from our GitHub Releases directly into your local ~/.cache/async_batch_faker/ directory.

It only downloads once. Every subsequent run loads the locale from your local NVMe/SSD directly into memory at blistering speed.

## 📦 Installation

```bash
pip install async-batch-faker
```

_(Requires Python 3.8+ and numpy)_

## 💻 Quick Start (3 Ways to Generate Data)

You don't need to be an expert in asyncio or numpy to use this library. We designed it to be as simple as possible.

### Level 1: Just give me a Python List (Beginners)

Generate tens of thousands of records instantly in standard Python, no async knowledge required.

```python
from async_batch_faker import AsyncBatchFaker

# Initialize with your preferred locale (defaults to en_US)
fake = AsyncBatchFaker(locale="ur_PK")

schema = {
    "id": fake.uuid4,
    "name": fake.full_name,
    "email": fake.email,
    "city": fake.city,
}

# Returns a standard list of dictionaries instantly
data = fake.generate(schema=schema, total=10000)
print(data[0])  # {'id': '...', 'name': '...', 'email': '...', 'city': '...'}
```

### Level 2: Export straight to CSV (Data Science)

Need a massive dataset for Pandas, Excel, or Kaggle? Stream it directly to a file without overloading your RAM.

```python
from functools import partial
from async_batch_faker import AsyncBatchFaker

fake = AsyncBatchFaker()

# Add custom arguments using functools.partial
schema = {
    "name": fake.full_name,
    "joined_at": partial(
        fake.date_between, start_date="2020-01-01", end_date="2025-01-01"
    ),
    "is_active": fake.boolean,
}

# Generates 1 MILLION rows and saves them to a file in ~8 seconds
fake.to_csv(schema=schema, total=1_000_000, filename="users.csv")
```

### Level 3: Async Database Seeding (Advanced/Pro)

If you are seeding a database, use the async batch generator to stream data without blocking your event loop. Perfect for aiosqlite, asyncpg, or motor.

```python
import asyncio
from async_batch_faker import AsyncBatchFaker

async def seed_db():
    fake = AsyncBatchFaker()
    schema = {"id": fake.uuid4, "email": fake.email, "ip": fake.ipv4}

    # Generates 500,000 records, yielding in chunks of 50,000
    batch_generator = fake.generate_batches(
        schema=schema, total=500000, batch_size=50000
    )

    async for batch in batch_generator:
        # Bulk-insert this batch to your database here
        # await db.executemany(query, batch)
        print(f"Inserted {len(batch)} records...")

if __name__ == "__main__":
    asyncio.run(seed_db())
```

## 🔍 Exploring the Data (No Guessing Required)

Because async-batch-faker dynamically loads hundreds of datasets directly from localized text files, you might wonder exactly what fields you can generate. We built helper methods directly into the engine so you never have to guess or check the source code.

### View all available data fields

```python
from async_batch_faker import AsyncBatchFaker

fake = AsyncBatchFaker(locale="en_US")

# Prints an alphabetical list of EVERY provider you can use!
# Examples: 'color_name', 'cryptocurrency_code', 'mime_type', 'job_title'
print(fake.get_providers())
```

### View all supported countries/locales

```python
# Prints a list of all supported locales (e.g., 'ur_PK', 'fr_FR', 'ja_JP')
print(AsyncBatchFaker.available_locales())
```

## 🛡️ Typo Protection

If you misspell a provider, the engine won't just crash with a cryptic error—it will analyze your typo and suggest the correct field automatically.

```python
fake.colr(size=100)
# AttributeError: 'AsyncBatchFaker' has no provider 'colr'. Did you mean 'color_name'?
# 💡 Tip: Run `print(fake.get_providers())` to see all available datasets.
```

## 📝 License

MIT License. Created by Kashan Haider.
