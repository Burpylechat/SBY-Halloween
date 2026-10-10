import os
import asyncio
import json


#func to fix a bug, on windows only ofc ;)
if os.name == "nt":  # Only execute on Windows
    def fix_encoding(obj):
        #the func that encode well everything; bcs we are french, we use é, à, è
            if isinstance(obj, dict):
                return {fix_encoding(k): fix_encoding(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [fix_encoding(item) for item in obj]
            elif isinstance(obj, str):
                try:
                    return obj.encode('latin-1').decode('utf-8')
                except UnicodeEncodeError:
                    return obj
                except UnicodeDecodeError:
                    return obj
            else:
                return obj

else:
    def fix_encoding(obj):            
        return obj

# Function to open JSON data
def open_json(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return fix_encoding(json.load(f))
    return {}

# Function to save JSON data
def save_json(file_path: str, data: dict, ):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

default_inventory = {
    "started" : True,
    "energie" : 100,
    "last_reset" : 0,
    "points" : 0,
    "yokai" : {},
    "coin" : {},
    "room" : "main",
    "yokai aggressif" : {
        "Activated" : False,
        "Yokai" : None
    }
}

pieces = ["Salon", "Cuisine", "Chambre", "Salle de bain", "Bibliothèque", "Galerie", "Grenier"]
piece_property = open_json("./files/piece_property.json")
objets = []
for room in piece_property:
    for objet in piece_property[room]:
        objets.append(objet)
configuration = open_json("./files/bot-data.json")
images_piece = configuration["Images"]
room_description = open_json("./files/room_description.json")

coin_list = ["Pièce rouge", "Pièce orange", "Pièce jaune", "Pièce verte", "Pièce bleue ciel", "Pièce bleue", "Pièce mauve", "Pièce rose", "Pièce démoniaque"]
coin_proba = [12,12,12,12,12,12,12,12,4]

yokai_room = open_json("./files/yokai_room.json")

feminin = ["cuisine", "chambre", "salle de bain", "bibliothèque", "galerie", "cheminée", "table", "armoire", "commode"]    