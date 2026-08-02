import asyncio
import aiosqlite
import time
from functools import partial
from async_batch_faker import AsyncBatchFaker

async def seed_database():
    print("🚀 Initializing AsyncBatchFaker Engine...")
    fake = AsyncBatchFaker(locale="ur_PK")
    
    schema = {
        "id": fake.uuid4,
        "name": fake.full_name,
        "email": fake.email,
        "city": fake.city,
        "ip_address": fake.ipv4
    }
    
    total_records = 500_000
    batch_size = 50_000
    
    print("\n🗄️ Connecting to local SQLite database...")
    async with aiosqlite.connect("mock_data.db") as db:
        # 1. Setup the table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                city TEXT,
                ip_address TEXT
            )
        """)
        # Clear it if it already exists so we get a fresh run
        await db.execute("DELETE FROM users")
        await db.commit()
        
        # 2. Prepare the bulk insert query
        insert_query = """
            INSERT INTO users (id, name, email, city, ip_address)
            VALUES (:id, :name, :email, :city, :ip_address)
        """
        
        print(f"⚡ Seeding {total_records:,} records in batches of {batch_size:,}...")
        start_time = time.perf_counter()
        
        # 3. Generate and Insert concurrently
        async for batch in fake.generate_batches(schema=schema, total=total_records, batch_size=batch_size):
            await db.executemany(insert_query, batch)
            await db.commit()
            print(f"   -> Inserted batch of {len(batch):,} rows...")
            
        elapsed = time.perf_counter() - start_time
        print(f"\n✅ Successfully seeded {total_records:,} database rows in {elapsed:.3f} seconds!")

if __name__ == "__main__":
    asyncio.run(seed_database())