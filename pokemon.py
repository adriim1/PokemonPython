import requests
import os

class Pokemon:
    def __init__(self, id, nombre, tipos, stats, movimientos, species_url, imagen_url):
        self.id = id
        self.nombre = nombre.capitalize()
        self.tipos = tipos
        self.stats = stats
        self.hp_max = stats.get("hp", 0)
        self.hp_actual = self.hp_max
        self.esta_vivo = self.hp_actual > 0
        self.movimientos = movimientos
        self.species_url = species_url
        self.imagen_url = imagen_url

    def recibir_danio(self, cantidad):
        self.hp_actual = max(0, self.hp_actual - int(cantidad))
        self.esta_vivo = self.hp_actual > 0

    def atacar(self, oponente, mov):
        poder = mov.get('power') or 40
        ataque = self.stats.get('attack', 0)
        defensa_rival = oponente.stats.get('defense', 0)
        danio = max(5, poder + int(ataque * 0.5) - int(defensa_rival * 0.3))
        
        print(f"{self.nombre} usa {mov['name']}!")
        oponente.recibir_danio(danio)
        print(f"-> {oponente.nombre} pierde {danio} HP. (Quedan: {oponente.hp_actual})")

def obtener_datos_pokemon(nombre_pkm):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre_pkm.lower().strip()}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        datos = res.json()
        
        stats = {s["stat"]["name"]: s["base_stat"] for s in datos["stats"]}
        tipos = ", ".join([t["type"]["name"] for t in datos["types"]])
        
        movs = []
        for m in datos["moves"][:4]:
            try:
                m_info = requests.get(m["move"]["url"], timeout=5).json()
                movs.append({"name": m["move"]["name"], "power": m_info.get("power")})
            except:
                movs.append({"name": m["move"]["name"], "power": 40})
            
        return Pokemon(
            id=datos["id"], 
            nombre=datos["name"], 
            tipos=tipos, 
            stats=stats, 
            movimientos=movs, 
            species_url=datos["species"]["url"],
            imagen_url=datos["sprites"]["front_default"]
        )
    except Exception as e:
        raise Exception(f"No se pudo encontrar al Pokemon: {e}")

def descargar_imagen(pokemon):
    if not os.path.exists("imagenes"):
        os.makedirs("imagenes")
    try:
        img_res = requests.get(pokemon.imagen_url, timeout=10)
        ruta = f"imagenes/{pokemon.nombre}.png"
        with open(ruta, 'wb') as f:
            f.write(img_res.content)
        return True
    except:
        return False

def buscar_evolucion(pokemon_actual):
    try:
        res_species = requests.get(pokemon_actual.species_url, timeout=10).json()
        chain_url = res_species["evolution_chain"]["url"]
        chain = requests.get(chain_url, timeout=10).json()["chain"]
        
        while chain and chain["species"]["name"] != pokemon_actual.nombre.lower():
            if chain["evolves_to"]:
                chain = chain["evolves_to"][0]
            else:
                return None
        if chain and chain["evolves_to"]:
            return obtener_datos_pokemon(chain["evolves_to"][0]["species"]["name"])
    except:
        pass
    return None