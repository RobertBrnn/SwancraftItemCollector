# SimplyMaRch Swancraft Item Collection Parser

This tool is the spiritual succesor to parser behind the earlier SimplyCollectible Spreadsheet made by SimplyMarch.
The tool allowes one to parse the NBT data from minecraft items and present it in a decent looking spreadsheet.



## Currently supported NBT-tags

- **custom_name**: The formatted custom name gets transformed into plaintext  
- **minecraft_id**: The item id get added to the table
- **unbreakable**: A boolean to indicate whether the item is unbreakable or not 
- **Trail**: *Swancraft server exclusive* Shows the trail you obtain when wearing the item 
- **custom_effect**: *Swancraft server exclusive* Shows the custom effect you obtain when wearing the item 
- **collection**: *Swancraft server exclusive* If relevant, shows the collection the item is part of, which number it is and what the total number in the collection is  
- **enchantments**: Shows the vanilla enchantments the items have
- **bundle/shulker/crossbow contents**: All items inside the item are also formatted nicely *and* shown seperately
- **attribute_modifier**: All special attribute modifiers are shown with their related slot and operation  

---



### Requirements:
- Python (>= 3.9)

Python Modules:
- pandas
- roman

### Usage

To feed the parser you'll need .txt files with the raw NBT data from minecraft. Specifically it is recommended to use the [Inventory Profiles Next](https://modrinth.com/mod/inventory-profiles-next) mod.
These should be in a seperate folder (without other files).

To use the parser you run the NBTParserCLI.py with the --input argument (this is a path to the input folder) and the --output argument (this is a path where the output should land).
`python <path to NBTParserCLI.py> --input <path to input folder> --output <path to output folder>`

e.g.
`python NBTParserCLI.py --input "./data" --output "./output"`
