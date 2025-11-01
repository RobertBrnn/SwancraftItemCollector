import os
import pandas as pd
import time

import NBTReader
import NBTProcessor
import NBTBeautifier
        
    
#%%
DATA_DIR = "./data"
OUTPUT_DIR = "./output"

#%%
tic = time.time()
dir_list = os.listdir(DATA_DIR)
#dir_list = ["elementsLightBlue.txt", "T-51b Power Armor.txt", "icharusWings.txt", "DivineBox.txt", "yellowpants.txt", "ecoDestroyer.txt"]
#dir_list = ["Fallout 1.txt"]

item_components = {}
for file in dir_list:
    nbt_data = NBTReader.read_nbt_file(f"{DATA_DIR}/{file}")
    
    item_components[file] = NBTReader.flatten_main_item(nbt_data)
    
toc = time.time()
print(f"Done parsing raw files {toc-tic:.2f}s")
tic = toc


#%%

modification_list = [
    {"apply_to": "minecraft:custom_name", "new_val": "custom_name_plaintext", "func": NBTProcessor.parse_formatted_text},
    {"apply_to": "CustomName", "new_val": "custom_name_plaintext", "func": NBTProcessor.parse_formatted_text},
    {"apply_to": "custom_name_plaintext", "new_val": "custom_name_plaintext", "func": lambda x: x.strip()},
    {"apply_to": "minecraft:lore", "new_val": "lore_plaintext", "func": NBTProcessor.parse_formatted_text},
    {"apply_to": "lore_plaintext", "new_val": "collection", "func": NBTProcessor.parse_collection},
    {"apply_to": "lore_plaintext", "new_val": "trail", "func": NBTProcessor.parse_custom_trail},
    {"apply_to": "lore_plaintext", "new_val": "custom_effect", "func": NBTProcessor.parse_custom_effects},
    {"apply_to": "minecraft:bundle_contents", "new_val": "contents", "func": NBTProcessor.flatten_bundle},
    {"apply_to": "minecraft:container", "new_val": "contents", "func": NBTProcessor.flatten_container},
    {"apply_to": "minecraft:charged_projectiles", "new_val": "contents", "func": NBTProcessor.flatten_bundle},
    ]

#%%
enhanced_items = NBTProcessor.add_values(item_components, modification_list)
flattened_items = NBTProcessor.flatten_items(enhanced_items)
unique_items = NBTProcessor.drop_duplicates(flattened_items)
beautified_items = NBTBeautifier.beautify_item(unique_items)
unique_beautified_items = NBTProcessor.drop_duplicates(beautified_items)

custom_items = [item for item in unique_beautified_items if item["name"] is not None]

toc = time.time()
print(f"Preparing items {toc-tic:.2f}s")


#%%
manual_modifications = [
    {"item_name": "Toxic Sludgehammer", "modifications": {"trail": "☣ ꓄ꋪꍏꀤ꒒ ꂦꎇ ꓄ꂦꊼꀤꉓ ꅏꍏꌗ꓄ꍟ ☣"}},
    {"item_name": "The Cloak of Death", "modifications":{"trail": "🦇 𝔽𝕒𝕕𝕚𝕟𝕘 🦇 𝔼𝕔𝕙𝕠 🦇 𝕋𝕣𝕒𝕚𝕝 🦇"}},
    ]

fixed_custom_items = sorted(NBTProcessor.apply_modification(custom_items, manual_modifications), key= lambda x: x["name"])


#%%
df = pd.DataFrame(custom_items)
df.to_csv(f"{OUTPUT_DIR}/batch1.csv", index=False)
#%%
import json
with open(f"{OUTPUT_DIR}/batch1.json", "w") as f:
    json.dump(custom_items, f)

toc = time.time()
print(f"Done writing json {toc-tic:.2f}s")

