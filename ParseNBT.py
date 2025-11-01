import re
import os
import pandas as pd
import roman
#%%

def read_nbt_file(path):
    try:
        with open(path, encoding="utf8") as file:
            component_string = file.read()
    except:
        with open(path, encoding="ansi") as file:
            component_string = file.read()
        
    return parse_components(component_string)

def parse_components(string, lvl = 1):
    string = string.strip()
    
    if lvl == 1: # Defined by using '=>' for assignments. Only one such assignment exists
        clean_string = re.sub("(list|int)\\[[0-9]+\\] ", "", string).strip()
        
        item_parts = clean_string.split("=>")
        
        item_dict = {item_parts[0]: parse_components(item_parts[1], lvl=2)}
        return item_dict
    
    elif lvl == 2: # Defined by using '->' for assignements and \n as delimiters
        item_parts = re.split('(?P<key>\\S+)\\s*?->', string[1:].strip())
        
        parts_dict = {k.strip():parse_components(v.strip(), 3) for k, v in zip(item_parts[1::2], item_parts[2::2])}

        return parts_dict
    
    elif lvl == 3: # Finally 'normal' json. Sometimes invalid though...
        add_quotes = re.sub(": ([-0-9.E]+[a-z])", ': "\\1"', string)
        try:
            return eval(add_quotes)
        except Exception as e:
            if e.msg == "'{' was never closed":
                return parse_components(add_quotes + "}", 3)
        
            elif e.msg == "invalid decimal literal":
                return parse_components('"'+add_quotes+'"', 3)
            else:         
                print(e)
                return "Couldn't Parse - "+add_quotes
            
def flatten_main_item(item):
    k = list(item.keys())[0]
    v = list(item.values())[0]
    v["minecraft_id"] = k.strip()
    return v
        
#%%
def parse_formatted_text(formatted_text):
    if isinstance(formatted_text, list):
        return "\n".join([parse_formatted_text(c) for c in formatted_text])
    elif isinstance(formatted_text, str):
        return formatted_text
    elif isinstance(formatted_text, dict):
        
        resultText = formatted_text["text"]
        
        if "extra" in formatted_text.keys():
            resultText += "".join([parse_formatted_text(c) for c in formatted_text["extra"]])

        return resultText
        
def parse_collection(lore):
    match_collection = re.findall(r"(?m)^[\n\s]*([\S\- ]+) ([0-9]+)/([0-9]+)[\n\s]*$", lore)
    
    if match_collection:
        if "Your limit" in match_collection[0][0]:
            return None
        return {"collection": match_collection[0][0], "num": match_collection[0][1], "total": match_collection[0][2]}
    else:
        match_collection = re.findall(r"(?m)^[\n\s]*([\S\- ]+) #([0-9]+)[\n\s]*$", lore)
        
        if match_collection:
            return {"collection": match_collection[0][0], "num": match_collection[0][1], "total": ""}

def parse_custom_trail(lore):
    match_trail = re.findall(r"(?mi)^[\n\s]*(.+Trail[^\n\w,.;].*)[\n\s]*$", lore)
    
    if match_trail:
        return match_trail[0]
    else:
        return None
    

def parse_custom_effects(lore):
    match_effects = re.findall(r"(?m)^[\n\s]*(CE.*\*)[\n\s]*$", lore)
    
    return match_effects
    
    
def flatten_bundle(bundle_contents):
    item_list = []
    
    for item in bundle_contents:
        item_components = item["components"]
        item_components["minecraft_id"] = item["id"].strip()
        item_components["count"] = item["count"]
    
        item_list.append(item_components)
    
    return item_list

    
def flatten_container(contents):
    item_list = []
    
    for item_slot in contents:
        item = item_slot["item"]
        item_components = {} if "components" not in item.keys() else item["components"]
        item_components["minecraft_id"] = item["id"].strip()
        item_components["count"] = item["count"]
    
        item_list.append(item_components)
    
    return item_list

def add_value(obj, apply_to, new_val, func):
    
    if isinstance(obj, list):
        return [add_value(x, apply_to, new_val, func) for x in obj]
    
    elif isinstance(obj, dict):
        if apply_to in obj.keys():
            obj[new_val] = func(obj[apply_to])
        
        return {k:add_value(v, apply_to, new_val, func) for k, v in obj.items()}
    else:
        return obj

def add_values(obj, modification_list = [{"apply_to":"", "new_val":"", "func":""}]):
    
    if isinstance(obj, list):
        return [add_values(x, modification_list) for x in obj]
    
    elif isinstance(obj, dict):
        
        for mod in modification_list:
            if mod["apply_to"] in obj.keys():
                obj[mod["new_val"]] = mod["func"](obj[mod["apply_to"]])
        
        return {k:add_values(v, modification_list) for k, v in obj.items()}
    else:
        return obj
    
def flatten_items(obj):
    item_list = []
    
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                if "minecraft_id" in item.keys():
                    item_list.append(item)
                
                if "contents" in item.keys():
                    item_list += flatten_items(item["contents"])
                    
    if isinstance(obj, dict):
        if "minecraft_id" in obj.keys():
            item_list.append(obj)
        
        for k, item in obj.items():
            
            if isinstance(item, (list, dict)):
                item_list += flatten_items(item)
            
    return item_list            
            
def drop_duplicates(lst):
    distinct_list = []
    
    for item in lst:
        if item not in distinct_list:
            distinct_list.append(item)
    return distinct_list

def get_if_exists(dictionary, key, alt = None):
    if key in dictionary.keys():
        return dictionary[key]
    else:
        return alt

def apply_modification(obj, modification_list):
            
        if isinstance(obj, list):
            return [apply_modification(x, modification_list) for x in obj]
        
        elif isinstance(obj, dict):
            for mod in modification_list:
                if obj["name"] == mod["item_name"]:
                    
                    for field, value in mod["modifications"].items():
                        obj[field] = value
                        
            return {k:apply_modification(v, modification_list) for k, v in obj.items()}
        else:
            return obj

#%%
def beautify_item(item):
    if isinstance(item, list):
        return [beautify_item(i) for i in item]
    elif isinstance(item, dict):       
        
        res_dict = {}
        res_dict["name"] = get_if_exists(item, "custom_name_plaintext")
        res_dict["minecraft_id"] = get_if_exists(item, "minecraft_id")
        
        collection = get_if_exists(item, "collection")
        if collection:
            res_dict["collection_name"] = collection["collection"]
            res_dict["collection_num"] = collection["num"]
            res_dict["collection_total"] = collection["total"]
        
        contents = get_if_exists(item, "contents")
        if contents:
            res_dict["contents"] = beautify_item(contents)
        
        enchantments = get_if_exists(item, "minecraft:enchantments")
        if enchantments:
            formatted_enchantments_list = []
            for k, v in enchantments.items():
                if v == 1:
                    formatted_enchantments_list.append(f"{k}")
                elif v <= 10:
                    formatted_enchantments_list.append(f"{k} {roman.toRoman(v)}")
                else:
                    formatted_enchantments_list.append(f"{k} {v}")
            formatted_enchantments = "\n".join(formatted_enchantments_list)
            formatted_enchantments = formatted_enchantments.replace("minecraft:", "")
            res_dict["enchantments"] = formatted_enchantments
            
        att_mod = get_if_exists(item, "minecraft:attribute_modifiers")
        if att_mod:
            sorted_atts = sorted(att_mod, key=lambda d: get_if_exists(d,'slot', "zzzz"))
            formatted_attributes = []
            prev_slot = ""
            for att in sorted_atts:
                att_value = eval(att["amount"][:-1])
                slot = get_if_exists(att, "slot", "any slot")
                if slot != prev_slot:
                    formatted_attributes.append(f"When on/in {slot}")
                
                att_type = att['type'].replace('minecraft:','')
                operation_sign_dict = {"add_value": "+", "add_multiplied_base": "base +", "add_multiplied_total": "total x"}
                operation_sign = operation_sign_dict[att['operation']]
                formatted_att = f"  {operation_sign}{att_value} {att_type}  "
                formatted_attributes.append(formatted_att)
                
                prev_slot = slot
                
            res_dict["attribute_modifiers"] = "\n".join(formatted_attributes)

        trail = get_if_exists(item, "trail")
        if trail:
            res_dict["trail"] = trail
        
        ce = get_if_exists(item, "custom_effect")
        if ce:
            formatted_ce = "\n".join(ce)
            res_dict["custom_effect"] = formatted_ce
        return res_dict

    
#%%
import time
tic = time.time()
dir_list = os.listdir("data")
#dir_list = ["elementsRed.txt"]

item_components = {}
for file in dir_list:
    #print(file)
    nbt_data = read_nbt_file(f"data/{file}")
    
    item_components[file] = flatten_main_item(nbt_data)
toc = time.time()
print(f"Done parsing raw files {toc-tic:.2f}s")
tic = toc


#%%

modification_list = [
    {"apply_to": "minecraft:custom_name", "new_val": "custom_name_plaintext", "func": parse_formatted_text},
    {"apply_to": "CustomName", "new_val": "custom_name_plaintext", "func": parse_formatted_text},
    {"apply_to": "custom_name_plaintext", "new_val": "custom_name_plaintext", "func": lambda x: x.strip()},
    {"apply_to": "minecraft:lore", "new_val": "lore_plaintext", "func": parse_formatted_text},
    {"apply_to": "lore_plaintext", "new_val": "collection", "func": parse_collection},
    {"apply_to": "lore_plaintext", "new_val": "trail", "func": parse_custom_trail},
    {"apply_to": "lore_plaintext", "new_val": "custom_effect", "func": parse_custom_effects},
    {"apply_to": "minecraft:bundle_contents", "new_val": "contents", "func": flatten_bundle},
    {"apply_to": "minecraft:container", "new_val": "contents", "func": flatten_container},
    ]

#%%
enhanced_items = add_values(item_components, modification_list)
flattened_items = flatten_items(enhanced_items)
unique_items = drop_duplicates(flattened_items)
beautified_items = beautify_item(unique_items)
unique_beautified_items = drop_duplicates(beautified_items)

custom_items = [item for item in unique_beautified_items if item["name"] is not None]

toc = time.time()
print(f"Preparing items {toc-tic:.2f}s")


#%%
manual_modifications = [
    {"item_name": "Toxic Sludgehammer", "modifications": {"trail": "☣ ꓄ꋪꍏꀤ꒒ ꂦꎇ ꓄ꂦꊼꀤꉓ ꅏꍏꌗ꓄ꍟ ☣"}}
    ]

fixed_custom_items = sorted(apply_modification(custom_items, manual_modifications), key= lambda x: x["name"])


#%%
df = pd.DataFrame(custom_items)
df.to_csv("staging/batch1.csv", index=False)
#%%
import json
with open("staging/batch1.json", "w") as f:
    json.dump(custom_items, f)

toc = time.time()
print(f"Done writing json {toc-tic:.2f}s")

#%%
z1= fixed_custom_items[14]
z2= fixed_custom_items[15]
z1["minecraft_id"] == z2["minecraft_id"]