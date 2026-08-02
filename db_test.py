import asyncio
from functools import partial
from async_batch_faker import AsyncBatchFaker

async def main():
    print("Initializing the ultimate engine...\n")
    # Let's hit the Pakistani data to prove it localized perfectly
    fake = AsyncBatchFaker(locale="ur_PK")
    
    # Look at these new dynamic fields we are passing!
    schema = {
        "id": fake.uuid4,
        "name": fake.full_name,
        "email": fake.email,
        "ip_address": fake.ipv4,
        "mac": fake.mac_address,
        "city": fake.city,                     # Auto-loaded from ur_PK/city.txt
        "job": fake.job,                       # Auto-loaded from ur_PK/job.txt
        "color": fake.color_name,              # Auto-loaded from global/color_name.txt
        "crypto": fake.cryptocurrency_code,    # Auto-loaded from global/cryptocurrency_code.txt
        "file_type": fake.mime_type,           # Auto-loaded from global/mime_type.txt
        "joined_at": partial(fake.date_between, start_date="2024-01-01", end_date="2025-01-01")
    }
    
    print("Blasting batch with omni-data...\n")
    async for batch in fake.generate_batches(schema=schema, total=5, batch_size=5):
        for row in batch:
            print(row)
            print("-" * 60)

if __name__ == "__main__":
    asyncio.run(main())