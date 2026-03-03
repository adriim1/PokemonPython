from pokemon import obtener_pokemon_desde_api, imprimir_pokemon


def pedir_nombre_pokemon(numero: int) -> str:
    return input(f"Introduce el nombre del Pokémon {numero}: ")


def elegir_movimiento(pokemon) -> dict:
    if not pokemon.movimientos:
        print(f"{pokemon.name} no tiene movimientos disponibles.")
        return {}

    print(f"Movimientos de {pokemon.name}:")
    for i, mov in enumerate(pokemon.movimientos, start=1):
        print(
            f"{i}. {mov.get('move_name')} "
            f"(power={mov.get('move_power')}, pp={mov.get('move_pp')})"
        )

    while True:
        try:
            opcion = int(input("Elige un movimiento (número): "))
            if 1 <= opcion <= len(pokemon.movimientos):
                return pokemon.movimientos[opcion - 1]
        except ValueError:
            pass
        print("Opción no válida, inténtalo de nuevo.")


def combate(pokemon1, pokemon2) -> None:
    turno = 1
    while pokemon1.esta_vivo and pokemon2.esta_vivo:
        print(f"\n--- Turno {turno} ---")
        print(f"{pokemon1.name}: {pokemon1.hp_actual} HP")
        print(f"{pokemon2.name}: {pokemon2.hp_actual} HP")

        print(f"\nTurno de {pokemon1.name}")
        mov1 = elegir_movimiento(pokemon1)
        pokemon1.atacar(pokemon2, mov1)

        if not pokemon2.esta_vivo:
            print(f"\n{pokemon2.name} se ha debilitado. ¡{pokemon1.name} gana!")
            break

        print(f"\nTurno de {pokemon2.name}")
        mov2 = elegir_movimiento(pokemon2)
        pokemon2.atacar(pokemon1, mov2)

        if not pokemon1.esta_vivo:
            print(f"\n{pokemon1.name} se ha debilitado. ¡{pokemon2.name} gana!")
            break

        turno += 1


def main() -> None:
    print("=== Batalla Pokémon ===")

    nombre1 = pedir_nombre_pokemon(1)
    nombre2 = pedir_nombre_pokemon(2)

    try:
        pokemon1 = obtener_pokemon_desde_api(nombre1)
        pokemon2 = obtener_pokemon_desde_api(nombre2)
    except Exception as e:
        print("Ha ocurrido un error al obtener los datos de la API:", e)
        return

    print("\n--- Pokémon 1 ---")
    imprimir_pokemon(pokemon1)

    print("\n--- Pokémon 2 ---")
    imprimir_pokemon(pokemon2)

    print("\n¿Quieres que se enfrenten? (s/n)")
    opcion = input().strip().lower()
    if opcion == "s":
        combate(pokemon1, pokemon2)
    else:
        print("Fin del programa.")


if __name__ == "__main__":
    main()

