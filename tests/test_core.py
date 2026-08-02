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