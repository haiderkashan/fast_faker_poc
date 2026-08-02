# ⚡ Async Batch Faker

A high-performance, asynchronous, vectorized mock data generator for Python.

Built to solve the bottleneck of seeding massive databases in modern async web frameworks. While standard `Faker` is great for generating a single row for unit testing, `Async Batch Faker` uses `numpy` and `asyncio` to blast hundreds of thousands of rows into your database in seconds.

**🚀 Benchmark:** Generates and yields 100,000 rows of mock data (UUID, Names, Emails, Booleans, Ages) in **~8.65 seconds**.

## Why use this?

- **Vectorized Generation:** Uses `numpy` under the hood to generate data in massive arrays, bypassing slow Python `for` loops.
- **Async Batching:** Yields data in chunks asynchronously, allowing your database driver (like `aiosqlite`, `asyncpg`, or `motor`) to insert rows while the next chunk is being generated.
- **Lightweight:** No massive datasets of XML/Barcode generators. Just the core data types you need to seed a database fast.
- **Locale Support:** Easily switch between regional datasets.

## Installation

```bash
pip install async-batch-faker
```

## Quickstart

```python
import asyncio
from functools import partial
from async_batch_faker import AsyncBatchFaker

async def main():
    # Initialize with default locale (en_US)
    fake = AsyncBatchFaker()

    # Define your dynamic schema
    schema = {
        "id": fake.uuid4,
        "full_name": fake.name,
        "email": fake.email,
        "is_active": fake.boolean,
        "age": partial(fake.age, min_age=18, max_age=45) # Custom arguments!
    }

    # Generate 100,000 records in batches of 10,000
    batch_generator = fake.generate_batches(schema=schema, total=100000, batch_size=10000)

    async for batch in batch_generator:
        # In a real app, you would bulk-insert this batch to your database here
        print(f"Received batch of {len(batch)} records!")
        print("First row:", batch[0])

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔍 Exploring the Data (No Guessing Required)

Because `async-batch-faker` dynamically loads thousands of datasets directly from text files, you might wonder exactly what fields you can generate.

We built helper methods directly into the engine so you never have to guess.

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
# Prints a list of all 100+ supported locales (e.g., 'ur_PK', 'fr_FR', 'ja_JP')
print(AsyncBatchFaker.available_locales())
```

### Typo Protection

If you misspell a provider, the engine won't just crash—it will analyze your typo and suggest the correct field automatically.

```python
fake.colr(size=100)
# AttributeError: 'AsyncBatchFaker' has no provider 'colr'. Did you mean 'color_name'?
```

## License

MIT License. Created by Kashan Haider.
