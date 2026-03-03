import json
from typing import List, Dict, Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request


class Pokemon:
    def __init__(
        self,
        name: str,
        descripcion: str,
        movimientos: List[Dict[str, Any]],
        tipos: List[str],
        stats: Dict[str, int],
    ) -> None:
        self.name = name
        self.descripcion = descripcion
        self.movimientos = movimientos
        self.tipos = tipos
        self.stats = stats
        self.hp_actual = stats.get("hp", 0)
        self.esta_vivo = self.hp_actual > 0

    def recibir_danio(self, cantidad: int) -> None:
        if cantidad < 0:
            cantidad = 0

        self.hp_actual -= cantidad

        if self.hp_actual <= 0:
            self.hp_actual = 0
            self.esta_vivo = False

    def atacar(self, otro_pokemon: "Pokemon", movimiento: Dict[str, Any]) -> None:
        poder = movimiento.get("move_power", 0) or 0
        ataque = self.stats.get("attack", 0)
        defensa_objetivo = otro_pokemon.stats.get("defense", 0)

        danio_base = poder + int(ataque * 0.5) - int(defensa_objetivo * 0.3)
        danio = max(1, danio_base)

        print(f"{self.name} usa {movimiento.get('move_name')} y hace {danio} de daño.")
        otro_pokemon.recibir_danio(danio)


def obtener_pokemon_desde_api(nombre: str) -> Pokemon:
    nombre = nombre.lower().strip()
    url_pokemon = f"https://pokeapi.co/api/v2/pokemon/{nombre}"

    req_pokemon = Request(
        url_pokemon,
        headers={"User-Agent": "pokemon-app/1.0"},
    )
    with urlopen(req_pokemon) as resp:
        data = json.load(resp)

    name = data["name"]

    tipos = [t["type"]["name"] for t in data.get("types", [])]

    stats_dict: Dict[str, int] = {}
    for s in data.get("stats", []):
        stat_name = s["stat"]["name"]
        base_stat = s["base_stat"]
        stats_dict[stat_name] = base_stat

    stats = {
        "hp": stats_dict.get("hp", 0),
        "attack": stats_dict.get("attack", 0),
        "defense": stats_dict.get("defense", 0),
        "special-attack": stats_dict.get("special-attack", 0),
        "special-defense": stats_dict.get("special-defense", 0),
        "speed": stats_dict.get("speed", 0),
    }

    species_url = data["species"]["url"]
    req_species = Request(
        species_url,
        headers={"User-Agent": "pokemon-app/1.0"},
    )
    with urlopen(req_species) as resp_species:
        data_species = json.load(resp_species)

    descripcion = "Sin descripción disponible."
    flavor_texts = data_species.get("flavor_text_entries", [])
    for entry in flavor_texts:
        if entry.get("language", {}).get("name") == "es":
            descripcion = entry.get("flavor_text", "").replace("\n", " ").replace("\f", " ")
            break
        elif entry.get("language", {}).get("name") == "en" and descripcion == "Sin descripción disponible.":
            descripcion = entry.get("flavor_text", "").replace("\n", " ").replace("\f", " ")

    movimientos_api = data.get("moves", [])[:4]
    movimientos: List[Dict[str, Any]] = []

    for move_entry in movimientos_api:
        move_name = move_entry["move"]["name"]
        move_url = move_entry["move"]["url"]

        try:
            req_move = Request(
                move_url,
                headers={"User-Agent": "pokemon-app/1.0"},
            )
            with urlopen(req_move) as move_resp:
                move_data = json.load(move_resp)

            movimientos.append(
                {
                    "move_name": move_name,
                    "move_power": move_data.get("power"),
                    "move_pp": move_data.get("pp"),
                }
            )
        except (HTTPError, URLError, ValueError):
            movimientos.append(
                {
                    "move_name": move_name,
                    "move_power": None,
                    "move_pp": None,
                }
            )

    return Pokemon(
        name=name,
        descripcion=descripcion,
        movimientos=movimientos,
        tipos=tipos,
        stats=stats,
    )


def imprimir_pokemon(pokemon: Pokemon) -> None:
    print("{")
    print(f'  "nombre": "{pokemon.name}",')
    print('  "tipos": [')
    for i, tipo in enumerate(pokemon.tipos):
        coma = "," if i < len(pokemon.tipos) - 1 else ""
        print(f'    "{tipo}"{coma}')
    print("  ],")
    print('  "movimientos": [')
    for i, mov in enumerate(pokemon.movimientos):
        coma = "," if i < len(pokemon.movimientos) - 1 else ""
        print("    {")
        print(f'      "move_name": "{mov.get("move_name")}",')
        print(f'      "move_power": {mov.get("move_power")},')
        print(f'      "move_pp": {mov.get("move_pp")}')
        print(f"    }}{coma}")
    print("  ],")
    print('  "stats": {')
    keys = list(pokemon.stats.keys())
    for i, (k, v) in enumerate(pokemon.stats.items()):
        coma = "," if i < len(keys) - 1 else ""
        print(f'    "{k}": {v}{coma}')
    print("  }")
    print("}")

