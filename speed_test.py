import time

print("1. Testing Import...")
t0 = time.time()
from async_batch_faker import AsyncBatchFaker
print(f"✅ Import took {time.time() - t0:.3f} seconds\n")

print("2. Testing Initialization...")
t1 = time.time()
fake = AsyncBatchFaker()
print(f"✅ Init took {time.time() - t1:.3f} seconds\n")

print("3. Testing First Generation...")
t2 = time.time()
schema = {"first_name": fake.first_name, "city": fake.city}
data = fake.generate(schema, total=100)
print(f"✅ Generation took {time.time() - t2:.3f} seconds\n")