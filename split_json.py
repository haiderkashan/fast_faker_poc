import json
import os

def split_monolith():
    print("🔪 Slicing the monolithic JSON...")
    
    # 1. Read the giant file one last time
    with open("src/async_batch_faker/packed_locales.json", "r", encoding="utf-8") as f:
        big_data = json.load(f)

    # 2. Create a new locales folder
    locales_dir = "src/async_batch_faker/locales"
    os.makedirs(locales_dir, exist_ok=True)

    # 3. Save each language as its own tiny JSON file
    for locale, providers in big_data.items():
        out_path = os.path.join(locales_dir, f"{locale}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(providers, f)
            
    print(f"✅ Split into {len(big_data)} separate lightweight files!")

if __name__ == "__main__":
    split_monolith()