from __future__ import annotations

import asyncio
import csv
import difflib
import json
import uuid
import os
import urllib.request
from importlib import resources
from pathlib import Path
from typing import ClassVar

import numpy as np
from faker import Faker


class AsyncBatchFaker:
    _cache: ClassVar[dict] = {}
    _faker_cache: ClassVar[dict] = {}  
    _providers_cache: ClassVar[dict] = {}  

    def __init__(self, locale: str = "en_US", seed: int | None = None):
        self.locale = locale
        self.seed = seed  
        self.rng = np.random.default_rng(seed)
        
        # We will lazy-load the JSON dictionaries only when requested
        self._locale_data = self._load_json_file(locale)
        self._global_data = self._load_json_file("global")

        if locale not in self.__class__._cache:
            self.__class__._cache[locale] = {}

        self.data = self.__class__._cache[locale]

    def _load_json_file(self, filename: str) -> dict:
        """Loads a specific locale JSON file into memory, downloading it if necessary."""
        # 1. Try loading from bundled local package files first
        try:
            with resources.files("async_batch_faker.locales").joinpath(f"{filename}.json").open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

        # Fallback for local testing if resources fail
        local_path = os.path.join(os.path.dirname(__file__), "locales", f"{filename}.json")
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # 2. Try loading from local user cache directory
        cache_dir = Path.home() / ".cache" / "async_batch_faker"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{filename}.json"
        
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass  # Corrupt cache, fallback to re-download

        # 3. Auto-download missing locale file from GitHub release assets
        url = f"https://github.com/haiderkashan/async_batch_faker/releases/download/v0.1.3-data/{filename}.json"
        
        try:
            print(f"🔄 Locale '{filename}' not found locally. Downloading from GitHub release...")
            urllib.request.urlretrieve(url, cache_path)
            
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {}

    @property
    def _faker(self):
        if self.locale not in self.__class__._faker_cache:
            fallback = Faker(self.locale)
            self.__class__._faker_cache[self.locale] = fallback

        if self.seed is not None:
            self.__class__._faker_cache[self.locale].seed_instance(self.seed)

        return self.__class__._faker_cache[self.locale]

    def _get_provider_array(self, provider_name: str) -> np.ndarray:
        if provider_name in self.data:
            return self.data[provider_name]

        # Lazy-load the specific JSON files on the very first data generation request
        if self._locale_data is None:
            self._locale_data = self._load_json_file(self.locale)
        if self._global_data is None:
            self._global_data = self._load_json_file("global")

        if self._locale_data and provider_name in self._locale_data:
            lines = self._locale_data[provider_name]
        elif self._global_data and provider_name in self._global_data:
            lines = self._global_data[provider_name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' has no provider '{provider_name}'.")

        array_data = np.array(lines)
        self.data[provider_name] = array_data
        return array_data

    def __getattr__(self, name: str):
        try:
            provider_array = self._get_provider_array(name)

            def dynamic_provider(size):
                return self.rng.choice(provider_array, size=size, replace=True)

            return dynamic_provider
        except AttributeError:
            pass  

        if hasattr(self._faker, name):
            return getattr(self._faker, name)

        if self.locale not in self.__class__._providers_cache:
            # Load keys purely for typo protection cache
            if self._locale_data is None:
                self._locale_data = self._load_json_file(self.locale)
            if self._global_data is None:
                self._global_data = self._load_json_file("global")
                
            providers = set(self._global_data.keys() if self._global_data else {})
            providers.update(self._locale_data.keys() if self._locale_data else {})
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
        """Returns locales. Note: With auto-downloading, all standard Faker locales are supported dynamically."""
        return ["en_US", "(Other locales download automatically on demand)"]

    def get_providers(self):
        """Returns a list of all available data providers for this locale."""
        if self.locale not in self.__class__._providers_cache:
            if self._locale_data is None:
                self._locale_data = self._load_json_file(self.locale)
            if self._global_data is None:
                self._global_data = self._load_json_file("global")
                
            dynamic_set = set(self._global_data.keys() if self._global_data else {})
            dynamic_set.update(self._locale_data.keys() if self._locale_data else {})
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

    # --- High-Speed Math & Logic Providers ---
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

    # --- Composite Providers (Mixing logic with arrays) ---
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