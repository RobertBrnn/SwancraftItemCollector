import roman
#%%
def format_decimal(value, num_decimals):
    
    rounded_val = round(value, num_decimals)
    int_rounded_val = int(rounded_val)

    return int_rounded_val if int_rounded_val == rounded_val else rounded_val


def get_if_exists(dictionary, key, alt = None):
    if key in dictionary.keys():
        return dictionary[key]
    else:
        return alt

def beautify_collection(item):
    
    if "collection" in item.keys() and item["collection"]:
        collection = item["collection"]
        return {
            "collection_name": collection["collection"],
            "collection_num": collection["num"],
            "collection_total": collection["total"],
            }
    else:
        return {}
    
def beautify_enchantments(item):
    
    if "minecraft:enchantments" in item.keys() and item["minecraft:enchantments"]:
        enchantments = item["minecraft:enchantments"]
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
        
        return {"enchantments": formatted_enchantments}
    else:
        return {}
    
def beautify_attribute_modifiers(item):
    
    if "minecraft:attribute_modifiers" in item.keys() and item["minecraft:attribute_modifiers"]:
        att_mod = item["minecraft:attribute_modifiers"]
        
        sorted_atts = sorted(att_mod, key=lambda d: get_if_exists(d,'slot', "zzzz"))
        formatted_attributes = []
        prev_slot = ""
        for att in sorted_atts:
            att_value = eval(att["amount"][:-1])
            att_value = format_decimal(att_value, 3)
            if att_value == 0:
                pass #next                
            slot = get_if_exists(att, "slot", "any slot")
            if slot != prev_slot:
                formatted_attributes.append(f"When on/in {slot}")
            
            att_type = att['type'].replace('minecraft:','')
            if att["operation"] == "add_value":
                formatted_att = f"  {'+' if att_value >=0 else ''}{att_value} {att_type}"
            elif att["operation"] =="add_multiplied_base":
                att_pct = att_value * 100
                att_pct = format_decimal(att_pct, 1)
                formatted_att = f"  {'+' if att_pct >=0 else ''}{att_pct}% {att_type}"
            elif att["operation"] == "add_multiplied_total":
                formatted_att = f"  total x{att_value+1} {att_type}"
            else:
                formatted_att = f"  Couldn't parse {att}"
            
            formatted_attributes.append(formatted_att)
            
            prev_slot = slot
            
        return {"attribute_modifiers": "\n".join(formatted_attributes)}
    else:
        return {}
        
def beautify_potion_contents(item):
        
    if "minecraft:potion_contents" in item.keys() and item["minecraft:potion_contents"]:
        potion_contents = item["minecraft:potion_contents"]
        effect_list = []
        if "potion" in potion_contents.keys():
            vanilla_potion = potion_contents["potion"].replace("minecraft:", "")
            effect_list.append(f"{vanilla_potion}")
        if "custom_effects" in potion_contents.keys():
            custom_effects = potion_contents["custom_effects"]
            for ce in custom_effects:
                effect_id = ce["id"].replace("minecraft:", "")
                dur = ce["duration"]
                if dur == -1:
                    dur = "inf"
                elif dur > 0 and dur != 1:
                    dur_min = int(dur/1200)
                    dur_sec = round((dur - dur_min*1200)/20)
                    dur = f" ({dur_min:02d}:{dur_sec:02d})"
                else:
                    dur = ""
                    
                amplifier = get_if_exists(ce, "amplifier", "0d")
                amplifier = roman.toRoman(eval(amplifier[:-1]))
                effect_list.append(f"{effect_id} {amplifier if amplifier != 'N' else ''}{dur}")
            
        return {
            "potion_effects": "\n".join(effect_list)
            }
    else:
        return {}

def beautify_item(item):
    if isinstance(item, list):
        return [beautify_item(i) for i in item]
    elif isinstance(item, dict):       
        
        res_dict = {}
        res_dict["name"] = get_if_exists(item, "custom_name_plaintext")
        res_dict["minecraft_id"] = get_if_exists(item, "minecraft_id")
        
        unbreakable = get_if_exists(item, "minecraft:unbreakable")
        res_dict["unbreakable"] = unbreakable is not None
        
        trail = get_if_exists(item, "trail")
        if trail:
            res_dict["trail"] = trail
            
        ce = get_if_exists(item, "custom_effect")
        if ce:
            formatted_ce = "\n".join(ce)
            res_dict["custom_effect"] = formatted_ce
        
        res_dict = res_dict | beautify_collection(item)
        
        res_dict = res_dict | beautify_enchantments(item)

        res_dict = res_dict | beautify_attribute_modifiers(item)
        
        res_dict = res_dict | beautify_potion_contents(item)
        
        contents = get_if_exists(item, "contents")
        if contents:
            res_dict["contents"] = beautify_item(contents)

        return res_dict