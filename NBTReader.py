import re

def read_nbt_file(path):
    # Simplistic way to ensure all emojis en special symbols are read in correctly 
    try:
        with open(path, encoding="utf8") as file:
            component_string = file.read()
    except:
        with open(path, encoding="ansi") as file:
            component_string = file.read()
    
    # Previous steps result in huge string. Parse this as a nested dict
    parsed_components = parse_components(component_string)
    return parsed_components

def parse_components(string, lvl = 1):
    # Parses NBT data into (nested) dict in multiple steps 
    
    string = string.strip()
    
    if lvl == 1: # Defined by using '=>' for assignments. Only one such assignment exists
        # NBT data contains data type hints such as 'list[9]', this is not neccesary for python
        clean_string = re.sub(r"(list|int)\[[0-9]+\] ", "", string).strip()
        
        item_parts = clean_string.split("=>")
        
        item_dict = {item_parts[0]: parse_components(item_parts[1], lvl=2)}
        return item_dict
    
    elif lvl == 2: # Defined by using '->' for assignements and \n as delimiters
        item_parts = re.split(r'(\S+)\s*?->', string[1:].strip())
        
        parts_dict = {k.strip():parse_components(v.strip(), 3) for k, v in zip(item_parts[1::2], item_parts[2::2])}

        return parts_dict
    
    elif lvl == 3: # Finally 'normal' json. Sometimes invalid though...

        # Numeric values get type hints (e.g. '1b' or '2.0d') these are not neccesary
        add_quotes = re.sub(": ([-0-9.E]+[a-z])", ': "\\1"', string)
        # Try to transform the string into a valid python variable and fix two know issues if needed
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
    # At the top level of the NBT data the ID is seperate from the components
    k = list(item.keys())[0]
    v = list(item.values())[0]
    v["minecraft_id"] = k.strip()
    return v
        