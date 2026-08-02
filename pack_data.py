import os
import json

def pack_locales():
    data_dir = "src/async_batch_faker/data"
    packed_data = {}

    print("📦 Packing locales...")
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.txt'):
                locale = os.path.basename(root)
                provider = file.replace('.txt', '')
                
                if locale not in packed_data:
                    packed_data[locale] = {}
                
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Read all lines, strip whitespace, and ignore empty lines
                    packed_data[locale][provider] = [line.strip() for line in f if line.strip()]

    output_file = "src/async_batch_faker/packed_locales.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(packed_data, f)
        
    print(f"✅ Successfully packed all data into {output_file}!")

if __name__ == "__main__":
    pack_locales()