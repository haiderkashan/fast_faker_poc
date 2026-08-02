from __future__ import annotations

import asyncio
import csv
import difflib
import uuid
from pathlib import Path
from typing import ClassVar

import numpy as np
from faker import Faker


class AsyncBatchFaker:
    # Class-level caches annotated correctly with ClassVar to satisfy Ruff RUF012
    _cache: ClassVar[dict] = {}
    _faker_cache: ClassVar[dict] = {}  # Cache for the standard Faker engine
    _providers_cache: ClassVar[dict] = {}  # Cache for the list of available providers

    def __init__(self, locale: str = "en_US", seed: int | None = None):
        self.locale = locale
        self.seed = seed  # Save this to seed the fallback faker later
        self.rng = np.random.default_rng(seed)

        # Initialize the cache dictionary for this locale if it doesn't exist
        if locale not in self.__class__._cache:
            self.__class__._cache[locale] = {}

        # Point instance data directly to the class cache
        self.data = self.__class__._cache[locale]

        current_dir = Path(__file__).parent
        self.global_dir = current_dir / "data" / "global"
        self.locale_dir = current_dir / "data" / self.locale

    @property
    def _faker(self):
        """Lazy-loads and caches the standard Faker engine."""
        if self.locale not in self.__class__._faker_cache:
            # This is the slow operation - now it only happens ONCE
            fallback = Faker(self.locale)
            self.__class__._faker_cache[self.locale] = fallback

        # Ensure the fallback faker respects our modern seed!
        if self.seed is not None:
            self.__class__._faker_cache[self.locale].seed_instance(self.seed)

        return self.__class__._faker_cache[self.locale]

    def _get_provider_array(self, provider_name: str) -> np.ndarray:
        """Lazy loads a provider's data from disk only if it isn't cached."""
        # 1. If it's already in the cache, return it instantly (Zero I/O)
        if provider_name in self.data:
            return self.data[provider_name]

        # 2. If not, figure out the path (Locale overrides Global)
        file_path = self.locale_dir / f"{provider_name}.txt"
        if not file_path.exists():
            file_path = self.global_dir / f"{provider_name}.txt"

        if not file_path.exists():
            raise AttributeError(f"'{self.__class__.__name__}' has no provider '{provider_name}'.")

        # 3. Read the file, convert to NumPy array, and save to cache
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            array_data = np.array(lines)
            self.data[provider_name] = array_data  # Saves to class _cache automatically
            return array_data
        except (OSError, UnicodeDecodeError):
            raise ValueError(f"Failed to load data for provider '{provider_name}'")

    # --- The Magic "Catch-All" Provider ---
    def __getattr__(self, name: str):
        # 1. First, check if it's a known numpy array method
        try:
            provider_array = self._get_provider_array(name)

            def dynamic_provider(size):
                # Using self.rng.choice directly accessing the C-level array
                return self.rng.choice(provider_array, size=size, replace=True)

            return dynamic_provider
        except AttributeError:
            pass  # Move on to the fallback/suggestion logic if the provider doesn't exist

        # 2. Check if the standard Faker has it (e.g., uuid4, boolean)
        if hasattr(self._faker, name):
            return getattr(self._faker, name)

        # 3. Typo Protection - Use a cached list of providers!
        if self.locale not in self.__class__._providers_cache:
            providers = set()
            if self.global_dir.exists():
                providers.update(f.stem for f in self.global_dir.glob("*.txt"))
            if self.locale_dir.exists():
                providers.update(f.stem for f in self.locale_dir.glob("*.txt"))
            self.__class__._providers_cache[self.locale] = list(providers)

        available = self.__class__._providers_cache.get(self.locale, [])
        matches = difflib.get_close_matches(name, available, n=1, cutoff=0.7)
        
        if matches:
            raise AttributeError(
                f"'{self.__class__.__name__}' has no provider '{name}'. Did you mean '{matches[0]}'?"
            )

        raise AttributeError(f"'{self.__class__.__name__}' has no provider '{name}'.")

    @staticmethod
    def available_locales():
        """Returns a list of all downloaded locales in the data folder."""
        data_dir = Path(__file__).parent / "data"
        if not data_dir.exists():
            return []
        locales = [
            d.name for d in data_dir.iterdir() if d.is_dir() and d.name != "global"
        ]
        return sorted(locales)

    def get_providers(self):
        """Returns a list of all available data providers for this locale."""
        # Use the cache we just built in __getattr__ for blistering speed
        if self.locale not in self.__class__._providers_cache:
            dynamic_set = set()
            if self.global_dir.exists():
                dynamic_set.update(f.stem for f in self.global_dir.glob("*.txt"))
            if self.locale_dir.exists():
                dynamic_set.update(f.stem for f in self.locale_dir.glob("*.txt"))
            self.__class__._providers_cache[self.locale] = list(dynamic_set)
            
        dynamic = self.__class__._providers_cache[self.locale]

        # The hardcoded math/logic providers
        hardcoded = [
            "age",
            "boolean",
            "uuid4",
            "ipv4",
            "mac_address",
            "credit_card_visa",
            "date_between",
            "full_name",
            "email",
        ]
        return sorted(dynamic + hardcoded)

    def __dir__(self):
        """Overrides built-in dir() to show dynamic providers in IDEs and terminals."""
        return super().__dir__() + self.get_providers()

    # --- High-Speed Math & Logic Providers (The ones we didn't download) ---
    def age(self, size, min_age=18, max_age=65):
        return self.rng.integers(min_age, max_age, size=size)

    def boolean(self, size):
        return self.rng.choice([True, False], size=size)

    def uuid4(self, size):
        return np.array([str(uuid.uuid4()) for _ in range(size)])

    def ipv4(self, size):
        p1 = self.rng.integers(1, 255, size=size).astype(str)
        p2 = self.rng.integers(0, 255, size=size).astype(str)
        p3 = self.rng.integers(0, 255, size=size).astype(str)
        p4 = self.rng.integers(1, 255, size=size).astype(str)
        return np.char.add(
            np.char.add(p1, "."),
            np.char.add(p2, np.char.add(".", np.char.add(p3, np.char.add(".", p4)))),
        )

    def mac_address(self, size):
        choices = np.array([f"{i:02x}" for i in range(256)])
        blocks = [self.rng.choice(choices, size=size) for _ in range(6)]
        mac = blocks[0]
        for block in blocks[1:]:
            mac = np.char.add(mac, ":")
            mac = np.char.add(mac, block)
        return mac

    def credit_card_visa(self, size):
        prefix = np.full(size, "4")
        digits = self.rng.integers(100000000000000, 999999999999999, size=size).astype(str)
        return np.char.add(prefix, digits)

    def date_between(self, size, start_date="2020-01-01", end_date="2025-01-01"):
        start = np.datetime64(start_date, "s")
        end = np.datetime64(end_date, "s")
        delta_seconds = int(np.uint64(end - start))
        random_seconds = self.rng.integers(0, delta_seconds, size=size)
        random_dates = start + random_seconds.astype("timedelta64[s]")
        return np.datetime_as_string(random_dates, unit="s")

    # --- Composite Providers (Mixing logic with downloaded arrays) ---
    def full_name(self, size):
        try:
            firsts = self.rng.choice(self._get_provider_array("first_name"), size=size, replace=True)
            lasts = self.rng.choice(self._get_provider_array("last_name"), size=size, replace=True)
            return np.char.add(np.char.add(firsts, " "), lasts)
        except AttributeError:
            return np.full(size, "Unknown Name")

    def email(self, size):
        try:
            firsts = self.rng.choice(self._get_provider_array("first_name"), size=size, replace=True)
            clean_names = np.char.lower(firsts)
            domains = self.rng.choice(self._get_provider_array("free_email_domain"), size=size, replace=True)
            return np.char.add(np.char.add(clean_names, "@"), domains)
        except AttributeError:
            return np.full(size, "unknown@email.com")

    # --- The Batcher ---
    async def generate_batches(self, schema, total, batch_size):
        batches = total // batch_size
        remainder = total % batch_size
        sizes = [batch_size] * batches
        if remainder > 0:
            sizes.append(remainder)

        for current_size in sizes:
            column_data = {}
            for column_name, generator_function in schema.items():
                column_data[column_name] = generator_function(size=current_size)

            keys = list(column_data.keys())
            arrays = [arr.tolist() for arr in column_data.values()]

            batch_records = [
                {keys[i]: value for i, value in enumerate(row)} for row in zip(*arrays)
            ]
            yield batch_records
            await asyncio.sleep(0)

    def generate(self, schema, total):
        """
        BEGINNER FRIENDLY: Generates mock data synchronously and returns a standard Python list.
        No asyncio or batching knowledge required!

        Example:
            records = fake.generate({"name": fake.full_name}, total=100)
        """

        async def _run_sync():
            results = []
            # We use one massive batch for speed since they just want a list
            async for batch in self.generate_batches(schema, total, batch_size=total):
                results.extend(batch)
            return results

        return asyncio.run(_run_sync())

    def to_csv(self, schema, total, filename="mock_data.csv", batch_size=100_000):
        """
        BEGINNER FRIENDLY: Generates mock data and streams it directly to a CSV file.

        Example:
            fake.to_csv({"name": fake.full_name}, total=1_000_000, filename="users.csv")
        """

        async def _run_export():
            with open(filename, mode="w", newline="", encoding="utf-8") as f:  # noqa: ASYNC230
                writer = csv.DictWriter(f, fieldnames=list(schema.keys()))
                writer.writeheader()

                print(f"✍️ Generating {total:,} rows and saving to {filename}...")
                async for batch in self.generate_batches(schema, total, batch_size):
                    writer.writerows(batch)
                print("✅ CSV Export Complete!")

        asyncio.run(_run_export())