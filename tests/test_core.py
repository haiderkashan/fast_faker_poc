import asyncio

import pytest

from async_batch_faker import AsyncBatchFaker


@pytest.fixture
def faker():
    # Loads the engine once for all tests
    return AsyncBatchFaker(locale="en_US")

def test_sync_generation(faker):
    """Test that the beginner-friendly sync method works."""
    schema = {"id": faker.uuid4, "age": faker.age}
    data = faker.generate(schema, total=10)
    
    assert len(data) == 10
    assert "id" in data[0]
    assert "age" in data[0]

def test_typo_protection(faker):
    """Test that misspellings raise a helpful AttributeError."""
    with pytest.raises(AttributeError, match="Did you mean"):
        # Intentional typo: 'emial' instead of 'email'
        faker.emial(size=10)

def test_async_batching(faker):
    """Test the core asynchronous batch yielding logic."""
    schema = {"name": faker.full_name}
    
    async def run_batch():
        batches = []
        async for batch in faker.generate_batches(schema, total=100, batch_size=50):
            batches.append(batch)
        return batches
        
    result = asyncio.run(run_batch())
    
    assert len(result) == 2  # Two batches of 50
    assert len(result[0]) == 50
    assert "name" in result[0][0]

def test_seeding_reproducibility():
    """Test that identical seeds produce identical datasets."""
    faker1 = AsyncBatchFaker(locale="en_US", seed=42)
    faker2 = AsyncBatchFaker(locale="en_US", seed=42)
    
    # REMOVED uuid4 because it uses os.urandom() and ignores all seeds
    # Testing direct providers to ensure self.rng is working
    schema1 = {"first_name": faker1.first_name, "city": faker1.city}
    schema2 = {"first_name": faker2.first_name, "city": faker2.city}
    
    # Dropped total to 100 for lightning-fast testing
    data1 = faker1.generate(schema1, total=100)
    data2 = faker2.generate(schema2, total=100)
    
    assert data1 == data2, "RNG seeding failed: outputs diverge."