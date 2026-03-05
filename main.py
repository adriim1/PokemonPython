import os
from pokemon import obtener_datos_pokemon, buscar_evolucion, descargar_imagen
from excel_manager import inicializar_excel, guardar_pokemon_excel, registrar_victoria_excel, obtener_resumen_pokedex

def elegir_ataque(pkm):
    print(f"\nTurno de {pkm.nombre}:")
    for i, m in enumerate(pkm.movimientos):
        print(f"{i+1}. {m['name']} (Poder: {m['power'] or '?'})")
    while True:
        try:
            idx = int(input("Selecciona ataque (1-4): ")) - 1
            if 0 <= idx < len(pkm.movimientos): return pkm.movimientos[idx]
        except: pass
        print("Opcion invalida.")

def preparar_pokemon(mensaje):
    nombre = input(mensaje)
    pkm = obtener_datos_pokemon(nombre)
    descargar_imagen(pkm)
    guardar_pokemon_excel(pkm)
    return pkm

def mostrar_album():
    if not os.path.exists("imagenes"):
        print("\nEl album esta vacio todavia.")
        return
    
    fotos = [f.replace(".png", "") for f in os.listdir("imagenes") if f.endswith(".png")]
    total_objetivo = 151
    
    print(f"\n{'='*40}")
    print(f"ALBUM DE CROMOS - PROGRESO: {len(fotos)}/{total_objetivo}")
    print(f"{'='*40}")
    
    resumen = obtener_resumen_pokedex()
    if resumen:
        print("Categorias capturadas:")
        for t, c in resumen.items():
            print(f"  - {t.capitalize()}: {c}")
    
    print("\nColeccion actual:")
    for i in range(0, len(fotos), 3):
        fila = fotos[i:i+3]
        print("  " + " | ".join(f"{p:<12}" for p in fila))
    print("="*40)

def modo_combate():
    try:
        p1 = preparar_pokemon("Nombre Pokemon 1: ")
        p2 = preparar_pokemon("Nombre Pokemon 2: ")
        print(f"\n--- COMBATE: {p1.nombre} vs {p2.nombre} ---")
        while p1.esta_vivo and p2.esta_vivo:
            p1.atacar(p2, elegir_ataque(p1))
            if not p2.esta_vivo: break
            p2.atacar(p1, elegir_ataque(p2))
        ganador = p1 if p1.esta_vivo else p2
        print(f"\nEL GANADOR ES: {ganador.nombre}")
        registrar_victoria_excel(ganador.nombre)
    except Exception as e:
        print(f"Error en combate: {e}")

def modo_evolucion():
    nombre = input("¿Que Pokemon quieres evolucionar?: ")
    try:
        pkm = obtener_datos_pokemon(nombre)
        print(f"Buscando evolucion para {pkm.nombre}...")
        evo = buscar_evolucion(pkm)
        if evo:
            print(f"El Pokemon {pkm.nombre} ha evolucionado a {evo.nombre}")
            descargar_imagen(evo)
            guardar_pokemon_excel(evo, "Evolucionado")
        else:
            print(f"El Pokemon {pkm.nombre} no tiene mas evoluciones.")
    except Exception as e:
        print(f"Error en evolucion: {e}")

def main():
    inicializar_excel()
    while True:
        print("\n--- MENU POKEMON ---")
        print("1. Combatir")
        print("2. Evolucionar")
        print("3. Ver Album")
        print("4. Salir")
        op = input("Selecciona una opcion: ")

        if op == "1":
            modo_combate()
        elif op == "2":
            modo_evolucion()
        elif op == "3":
            mostrar_album()
        elif op == "4":
            print("Cerrando programa.")
            break
        else:
            print("Opcion no valida.")

if __name__ == "__main__":
    main()