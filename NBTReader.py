import re

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
        