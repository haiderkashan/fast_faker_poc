import numpy as np
import asyncio
import uuid
import difflib
import csv
from pathlib import Path

class AsyncBatchFaker:
    def __init__(self, locale="en_US"):
        self.locale = locale
        self.data = {}
        
        current_dir = Path(__file__).parent
        self.global_dir = current_dir / "data" / "global"
        self.locale_dir = current_dir / "data" / self.locale
        
        print(f"Loading Omni-Heist datasets for {self.locale}...")
        self._load_datasets()

    def _load_datasets(self):
        # 1. Load everything from the global folder first
        if self.global_dir.exists():
            for txt_file in self.global_dir.glob("*.txt"):
                self._load_txt(txt_file)
                
        # 2. Load locale-specific files (overriding global ones if they share a name)
        if self.locale_dir.exists():
            for txt_file in self.locale_dir.glob("*.txt"):
                self._load_txt(txt_file)
                
    def _load_txt(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            # The filename (e.g., "color_name") becomes the dynamic method name
            provider_name = file_path.stem 
            if lines:
                self.data[provider_name] = np.array(lines)
        except Exception:
            pass

    # --- The Magic "Catch-All" Provider ---
    def __getattr__(self, name):
        """
        Intercepts any method call. If it doesn't exist, it smartly suggests the closest match.
        """
        if name in self.data:
            def dynamic_provider(size):
                return np.random.choice(self.data[name], size=size)
            return dynamic_provider
        
        available = self.get_providers()
        matches = difflib.get_close_matches(name, available, n=1, cutoff=0.5)
        suggestion = f" Did you mean '{matches[0]}'?" if matches else ""
        
        error_msg = (
            f"'{self.__class__.__name__}' has no provider '{name}'.{suggestion}\n"
            f"💡 Tip: Run `print(fake.get_providers())` to see all available datasets."
        )
        raise AttributeError(error_msg)

    @staticmethod
    def available_locales():
        """Returns a list of all downloaded locales in the data folder."""
        data_dir = Path(__file__).parent / "data"
        if not data_dir.exists():
            return []
        locales = [d.name for d in data_dir.iterdir() if d.is_dir() and d.name != "global"]
        return sorted(locales)

    def get_providers(self):
        """Returns a list of all available data providers for this locale."""
        # The dynamic text file providers
        dynamic = list(self.data.keys())
        # The hardcoded math/logic providers
        hardcoded = [
            "age", "boolean", "uuid4", "ipv4", "mac_address", 
            "credit_card_visa", "date_between", "full_name", "email"
        ]
        return sorted(dynamic + hardcoded)

    def __dir__(self):
        """Overrides built-in dir() to show dynamic providers in IDEs and terminals."""
        return super().__dir__() + self.get_providers()

    # --- High-Speed Math & Logic Providers (The ones we didn't download) ---
    def age(self, size, min_age=18, max_age=65):
        return np.random.randint(min_age, max_age, size=size)
        
    def boolean(self, size):
        return np.random.choice([True, False], size=size)
        
    def uuid4(self, size):
        return np.array([str(uuid.uuid4()) for _ in range(size)])

    def ipv4(self, size):
        p1 = np.random.randint(1, 255, size=size).astype(str)
        p2 = np.random.randint(0, 255, size=size).astype(str)
        p3 = np.random.randint(0, 255, size=size).astype(str)
        p4 = np.random.randint(1, 255, size=size).astype(str)
        return np.char.add(np.char.add(p1, "."), 
               np.char.add(p2, np.char.add(".", 
               np.char.add(p3, np.char.add(".", p4)))))

    def mac_address(self, size):
        choices = np.array([f"{i:02x}" for i in range(256)])
        blocks = [np.random.choice(choices, size=size) for _ in range(6)]
        mac = blocks[0]
        for block in blocks[1:]:
            mac = np.char.add(mac, ":")
            mac = np.char.add(mac, block)
        return mac

    def credit_card_visa(self, size):
        prefix = np.full(size, "4")
        digits = np.random.randint(100000000000000, 999999999999999, size=size).astype(str)
        return np.char.add(prefix, digits)

    def date_between(self, size, start_date="2020-01-01", end_date="2025-01-01"):
        start = np.datetime64(start_date, 's')
        end = np.datetime64(end_date, 's')
        delta_seconds = int(np.uint64(end - start))
        random_seconds = np.random.randint(0, delta_seconds, size=size)
        random_dates = start + random_seconds.astype('timedelta64[s]')
        return np.datetime_as_string(random_dates, unit='s')

    # --- Composite Providers (Mixing logic with downloaded arrays) ---
    def full_name(self, size):
        if "first_name" in self.data and "last_name" in self.data:
            firsts = np.random.choice(self.data["first_name"], size=size)
            lasts = np.random.choice(self.data["last_name"], size=size)
            return np.char.add(np.char.add(firsts, " "), lasts)
        return np.full(size, "Unknown Name")

    def email(self, size):
        if "first_name" in self.data and "free_email_domain" in self.data:
            firsts = np.random.choice(self.data["first_name"], size=size)
            clean_names = np.char.lower(firsts)
            domains = np.random.choice(self.data["free_email_domain"], size=size)
            return np.char.add(np.char.add(clean_names, "@"), domains)
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
                {keys[i]: value for i, value in enumerate(row)}
                for row in zip(*arrays)
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
        import csv
        
        async def _run_export():
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(schema.keys()))
                writer.writeheader()
                
                print(f"✍️ Generating {total:,} rows and saving to {filename}...")
                async for batch in self.generate_batches(schema, total, batch_size):
                    writer.writerows(batch)
            print("✅ CSV Export Complete!")
                    
        asyncio.run(_run_export())    