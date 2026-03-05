import tkinter as tk
from tkinter import messagebox, Toplevel, ttk
from PIL import Image, ImageTk
import os
import random
from pokemon import obtener_datos_pokemon, buscar_evolucion, descargar_imagen
from excel_manager import inicializar_excel, guardar_pokemon_excel, registrar_victoria_excel

class PokemonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SISTEMA POKEMON")
        self.root.geometry("500x650")
        
        inicializar_excel()

        tk.Label(self.root, text="GESTOR POKEMON", font=("Arial", 16, "bold")).pack(pady=10)
        self.entry_nombre = tk.Entry(self.root, font=("Arial", 12))
        self.entry_nombre.pack(pady=5)

        tk.Button(self.root, text="BUSCAR Y REGISTRAR", command=self.buscar, width=25).pack(pady=5)
        tk.Button(self.root, text="EVOLUCIONAR", command=self.evolucionar, width=25).pack(pady=5)
        tk.Button(self.root, text="MODO COMBATE", command=self.ventana_pre_combate, width=25, bg="#ffcccb").pack(pady=5)
        tk.Button(self.root, text="VER ÁLBUM VISUAL", command=self.ver_album_grafico, width=25, bg="#ccffcc").pack(pady=5)
        tk.Button(self.root, text="ABRIR EXCEL", command=self.abrir_excel, width=25).pack(pady=5)

        self.canvas_img_main = tk.Label(self.root)
        self.canvas_img_main.pack(pady=10)
        self.label_info = tk.Label(self.root, text="Esperando entrada...")
        self.label_info.pack()

    def mostrar_imagen(self, nombre):
        ruta = f"imagenes/{nombre.capitalize()}.png"
        if os.path.exists(ruta):
            img = Image.open(ruta).resize((150, 150))
            img_tk = ImageTk.PhotoImage(img)
            self.canvas_img_main.config(image=img_tk)
            self.canvas_img_main.image = img_tk

    def buscar(self):
        try:
            pkm = obtener_datos_pokemon(self.entry_nombre.get())
            descargar_imagen(pkm)
            guardar_pokemon_excel(pkm)
            self.mostrar_imagen(pkm.nombre)
            self.label_info.config(text=f"{pkm.nombre} registrado con éxito.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def evolucionar(self):
        try:
            pkm = obtener_datos_pokemon(self.entry_nombre.get())
            evo = buscar_evolucion(pkm)
            if evo:
                descargar_imagen(evo)
                guardar_pokemon_excel(evo, "Evolucionado")
                self.mostrar_imagen(evo.nombre)
                self.label_info.config(text=f"¡Ha evolucionado a {evo.nombre}!")
            else: messagebox.showinfo("Info", "Este Pokémon no tiene más evoluciones.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ventana_pre_combate(self):
        v = Toplevel(self.root)
        v.title("Preparar Arena")
        v.geometry("300x200")
        tk.Label(v, text="Pokémon 1:").pack()
        e1 = tk.Entry(v); e1.pack()
        tk.Label(v, text="Pokémon 2:").pack()
        e2 = tk.Entry(v); e2.pack()
        tk.Button(v, text="EMPEZAR DUELO", command=lambda: self.preparar_duelo(v, e1.get(), e2.get())).pack(pady=10)

    def preparar_duelo(self, ventana_pre, n1, n2):
        try:
            p1 = obtener_datos_pokemon(n1)
            p2 = obtener_datos_pokemon(n2)
            ventana_pre.destroy()
            self.arena(p1, p2)
        except Exception as e: messagebox.showerror("Error", str(e))

    def arena(self, p1, p2):
        v = Toplevel(self.root); v.geometry("400x500"); v.title(f"{p1.nombre} VS {p2.nombre}")
        lbl_p1 = tk.Label(v, text=f"{p1.nombre}: {p1.hp_actual} HP", font=("Arial", 12, "bold"))
        lbl_p1.pack(pady=5)
        lbl_p2 = tk.Label(v, text=f"{p2.nombre}: {p2.hp_actual} HP", font=("Arial", 12, "bold"))
        lbl_p2.pack(pady=5)
        txt_log = tk.Label(v, text="¡Que comience el duelo!", fg="blue")
        txt_log.pack(pady=10)
        frame_ataques = tk.Frame(v)
        frame_ataques.pack(pady=10)

        def refrescar_interfaz(atacante, defensor):
            for widget in frame_ataques.winfo_children(): widget.destroy()
            tk.Label(frame_ataques, text=f"Turno de {atacante.nombre}").pack()
            for mov in atacante.movimientos:
                tk.Button(frame_ataques, text=f"{mov['name']} (P:{mov['power'] or 40})", 
                        width=30, command=lambda m=mov: procesar_ataque(atacante, defensor, m)).pack(pady=2)

        def procesar_ataque(at, df, mv):
            danio = at.atacar(df, mv)
            lbl_p1.config(text=f"{p1.nombre}: {p1.hp_actual} HP")
            lbl_p2.config(text=f"{p2.nombre}: {p2.hp_actual} HP")
            txt_log.config(text=f"{at.nombre} usó {mv['name']} e hizo {danio} de daño")
            if not df.esta_vivo:
                messagebox.showinfo("Victoria", f"¡{at.nombre} gana el combate!")
                registrar_victoria_excel(at.nombre); v.destroy()
            else: refrescar_interfaz(df, at)

        refrescar_interfaz(p1, p2)

    def ver_album_grafico(self):
        if not os.path.exists("imagenes"):
            messagebox.showinfo("Álbum", "Aún no tienes imágenes registradas.")
            return

        v_album = Toplevel(self.root)
        v_album.title("Mi Álbum de Pokémon")
        v_album.geometry("600x500")

        main_frame = tk.Frame(v_album)
        main_frame.pack(fill=tk.BOTH, expand=1)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        second_frame = tk.Frame(canvas)
        canvas.create_window((0,0), window=second_frame, anchor="nw")

        archivos = [f for f in os.listdir("imagenes") if f.endswith(".png")]
        self.lista_fotos_album = []

        columna = 0
        fila = 0
        for nombre_archivo in archivos:
            nombre_pkm = nombre_archivo.replace(".png", "")
            ruta = f"imagenes/{nombre_archivo}"
            
            try:
                img = Image.open(ruta).resize((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                self.lista_fotos_album.append(img_tk)

                item_frame = tk.Frame(second_frame, bd=2, relief="groove", padx=5, pady=5)
                item_frame.grid(row=fila, column=columna, padx=10, pady=10)

                img_label = tk.Label(item_frame, image=img_tk)
                img_label.pack()
                tk.Label(item_frame, text=nombre_pkm, font=("Arial", 9, "bold")).pack()

                columna += 1
                if columna > 3:
                    columna = 0
                    fila += 1
            except:
                continue

    def abrir_excel(self):
        try: os.startfile("pokedex_datos.xlsx")
        except: messagebox.showerror("Error", "No se pudo abrir el archivo Excel.")

if __name__ == "__main__":
    root = tk.Tk(); app = PokemonApp(root); root.mainloop()