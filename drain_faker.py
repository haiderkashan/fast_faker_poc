import shutil
from pathlib import Path
from faker import Faker
from faker.config import AVAILABLE_LOCALES

def get_data_methods(fake_instance):
    """Dynamically discovers every method available in the Faker instance."""
    methods = []
    for attr_name in dir(fake_instance):
        # Skip private methods and internal config methods
        if attr_name.startswith('_') or attr_name in [
            'add_provider', 'cache_pattern', 'format', 'parse', 'provider', 
            'seed', 'seed_instance', 'seed_locale', 'set_formatter', 
            'random', 'generator', 'factories', 'providers', 'weights', 'locales', 'get_providers'
        ]:
            continue
            
        attr = getattr(fake_instance, attr_name)
        if callable(attr):
            methods.append(attr_name)
    return methods

def dump_everything(fake_instance, target_dir, iterations=2500):
    """Executes every discovered method and saves the output if it's text/numeric data."""
    target_dir.mkdir(parents=True, exist_ok=True)
    methods = get_data_methods(fake_instance)
    
    saved_files = 0
    for method_name in methods:
        method = getattr(fake_instance, method_name)
        data_set = set()
        
        for _ in range(iterations):
            try:
                # Attempt to call the method with NO arguments
                val = method()
                # We only want flat data: strings, ints, floats, booleans (skip dicts/tuples)
                if isinstance(val, (str, int, float, bool)):
                    data_set.add(str(val).strip())
            except Exception:
                # If it throws an error (e.g. requires arguments like date_between()), skip it instantly
                break
        
        # If we successfully captured data for this entity, write it to its own file!
        if data_set:
            with open(target_dir / f"{method_name}.txt", "w", encoding="utf-8") as f:
                # Sort it to remove randomness and keep it clean
                f.write("\n".join(sorted(data_set)))
            saved_files += 1
            
    print(f"      -> Extracted {saved_files} distinct entities.")

def omni_heist(base_dir):
    base_path = Path(base_dir)
    
    # 1. Nuke the old folder
    if base_path.exists():
        shutil.rmtree(base_path)
        print("💥 Wiped old data structure.")
        
    print("\n🌌 INITIATING OMNI-HEIST: EXTRACTING THE ENTIRE UNIVERSE...\n")
    
    # 2. Extract Global / Country-Independent Data
    print("Siphoning GLOBAL/INDEPENDENT Data (User Agents, Cryptos, File Extensions, etc.)...")
    # A default Faker instance holds all the base providers
    global_fake = Faker()
    dump_everything(global_fake, base_path / "global", iterations=4000)
    
    # 3. Extract Country-Specific Data
    print(f"\n🌍 Siphoning across {len(AVAILABLE_LOCALES)} localized countries...")
    for locale in AVAILABLE_LOCALES:
        print(f"   -> Siphoning {locale}...")
        try:
            locale_fake = Faker(locale)
            dump_everything(locale_fake, base_path / locale, iterations=2000)
        except Exception:
            print(f"      ❌ Failed to initialize {locale}, skipping.")
            continue

    print("\n🎉 OMNI-HEIST COMPLETE. You now possess absolutely everything.")

if __name__ == "__main__":
    # Point this to your engine's data directory
    omni_heist("async_batch_faker/data")