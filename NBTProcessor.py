import re

def parse_formatted_text(formatted_text):
    # Formatted text is stored in a series of lists and dicts
    # Loop through them to all the ['text'] fields
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
    # Collections are in the lore like '        Fallout Series 1/27'
    match_collection = re.findall(r"(?m)^[\n\s]*([\S\- ]+) ([0-9]+)/([0-9]+)[\n\s]*$", lore)
    
    if match_collection:
        # Prevent false positives for limited items: 'Your limit 1/2'
        if "Your limit" in match_collection[0][0]:
            return None
        collection_name = match_collection[0][0]
        # Sometimes lines start with a hidden period for formatting reasons, these should be cleaned up
        if collection_name[0] == ".":
            collection_name = collection_name[1:].strip()
        return {"collection": collection_name, "num": match_collection[0][1], "total": match_collection[0][2]}
    else:
        # Collections can also look like '      dirt series #2'
        match_collection = re.findall(r"(?m)^[\n\s]*([\S\- ]+) #([0-9]+)[\n\s]*$", lore)
        
        if match_collection:
            return {"collection": match_collection[0][0], "num": match_collection[0][1], "total": ""}

def parse_custom_trail(lore):
    # Trails look like '     
    match_trail = re.findall(r"(?mi)^[\n\s]*(.+Trail[^\n\w,.;].*)[\n\s]*$", lore)
    
    if match_trail:
        return match_trail[0]
    else:
        return None
    

def parse_custom_effects(lore):
    # Custom effects look like '     ☁ Dance of the Windborn Trail* ☁'
    match_effects = re.findall(r"(?m)^\W*CE *(.*)\*[\W]*$", lore)
    
    return match_effects
    
def flatten_bundle(bundle_contents):
    # Bundle contents are in nested dict with 'count'
    item_list = []
    
    for item in bundle_contents:
        item_components = item["components"]
        item_components["minecraft_id"] = item["id"].strip()
        item_components["count"] = item["count"]
    
        item_list.append(item_components)
    
    return item_list

def flatten_container(contents):
    # Bundle contents are in nested dict with 'count' and 'slot'

    item_list = []

    for item_slot in contents:
        item = item_slot["item"]
        item_components = {} if "components" not in item.keys() else item["components"]
        item_components["minecraft_id"] = item["id"].strip()
        item_components["count"] = item["count"]
    
        item_list.append(item_components)
    
    return item_list

def add_value(obj, apply_to, new_val, func):
    # Loop through nested obj to do new_val = func(apply_to)
    
    if isinstance(obj, list):
        return [add_value(x, apply_to, new_val, func) for x in obj]
    
    elif isinstance(obj, dict):
        if apply_to in obj.keys():
            obj[new_val] = func(obj[apply_to])
        
        return {k:add_value(v, apply_to, new_val, func) for k, v in obj.items()}
    else:
        return obj

def add_values(obj, modification_list = [{"apply_to":"", "new_val":"", "func":""}]):
    # Loop through nested obj to apply multiple modifications
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
    # Bundles, shulkers and crossbows can have contents
    # This function adds the contents to the list of items
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
    # Remove all duplicate values from the list
    distinct_list = []
    
    for item in lst:
        if item not in distinct_list:
            distinct_list.append(item)
    return distinct_list

def apply_modification(obj, modification_list):
    # Not all attributes can be extrapolated automatically
    # This function allowes one to manually set certain fields
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
