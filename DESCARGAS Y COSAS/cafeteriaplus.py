#Módulos y bibliotecas que serán utilizados 
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import os
import json
from datetime import datetime
import hashlib
import uuid

class SplashScreen:
    # Pantalla de presentación del programa
    def __init__(self, root, main_app_class):
        self.root = root 
        self.main_app_class = main_app_class # Clase principal que se ejecutará después
        self.root.title("Bienvenido")
        self.root.geometry("400x600") # Tamaño de la ventana 
        self.root.configure(bg="white") # Fondo blanco 
        
        try:
            self.root.iconbitmap("D:/DESCARGAS Y COSAS/cafe.ico") # Icono de la ventana
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")

        # Mostrar contenido del splash screen
        self.show_content()
        
        # Programa la transición después de 3 segundos
        self.root.after(3000, self.transition_to_main_app)

    def show_content(self):
        # Frame principal (ocupa toda la ventana)
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior para el texto (ocupa el espacio mínimo necesario)
        try:
            # Ruta de la imagen que reemplazará al texto (ej: "bienvenida.png")
            welcome_img_path = os.path.join("D:", "DESCARGAS Y COSAS", "bienvenido1.png")  
            welcome_img = Image.open(welcome_img_path)
            welcome_img = welcome_img.resize((350, 200), Image.Resampling.LANCZOS)  # Ajusta el tamaño según necesites
            self.welcome_img_tk = ImageTk.PhotoImage(welcome_img)
            
            # Muestrar la imagen (en lugar del Label de texto)
            welcome_label = tk.Label(
                main_frame, 
                image=self.welcome_img_tk, 
                bg="white"
            )
            welcome_label.pack(pady=(100, 20))  # Margen superior de 100px, inferior de 20px
        except Exception as e:
            print(f"Error al cargar imagen de bienvenida: {e}")
            # Si falla, muestra un texto alternativo (opcional)
            tk.Label(
                main_frame, 
                text="Bienvenido!!", 
                font=("Arial", 18, "bold"), 
                bg="white"
            ).pack(pady=(100, 5))
        
        # Frame inferior para la imagen (se expandirá hacia abajo)
        bottom_frame = tk.Frame(main_frame, bg="white")
        bottom_frame.pack(fill=tk.BOTH, expand=True)  # Ocupa todo el espacio restante
        
        # Carga y muestra la imagen EN LA PARTE INFERIOR
        try:
            img_path = os.path.join("D:", "DESCARGAS Y COSAS", "intro4.png")
            img = Image.open(img_path)
            img = img.resize((300, 350), Image.Resampling.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img)
            
            # Contenedor para centrar la imagen en el frame inferior
            img_container = tk.Frame(bottom_frame, bg="white")
            img_container.pack(expand=True, fill=tk.BOTH)
            
            img_label = tk.Label(
                img_container, 
                image=self.img_tk, 
                bg="white"
            )
            img_label.pack(side=tk.BOTTOM, pady=(0))  # Pegado al fondo con margen inferior
        except Exception as e:
            print(f"Error al cargar imagen de bienvenida: {e}")
            tk.Label(bottom_frame, text="Logo de la Cafetería", bg="white").pack(side=tk.BOTTOM)
        
    def transition_to_main_app(self):
        # Destruye la ventana actual
        self.root.destroy()
        
        # Crea la ventana principal y la aplicación
        root = tk.Tk()
        self.main_app_class(root)
        root.mainloop()

#Clase de gestión de usuarios del programa
class UserManager:
    def __init__(self):
        self.users_file = os.path.join("D:", "DESCARGAS Y COSAS", "users.json")
        self.current_user = None # Usuario actualmente logueado
        self.users = self.load_users() # Carga usuarios desde JSON
        
        # Crear usuario admin por defecto si no existe
        if not self.users:
            self.create_default_admin()
    
    def load_users(self):
        # Carga los usuarios desde el archivo JSON
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_users(self):
        # Guarda los usuarios en el archivo JSON
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los usuarios: {str(e)}")
    
    def create_default_admin(self):
        # Crea un usuario administrador por defecto
        default_user = {
            "id": str(uuid.uuid4()), 
            "username": "admin",
            "password_hash": self.hash_password("admin123"), 
            "is_owner": True, 
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        }
        self.users.append(default_user) 
        self.save_users()   
    
    def hash_password(self, password):
        # Hashea una contraseña
        salt = "cafeteria_salt"  
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def authenticate(self, username, password):
        # Autentica un usuario
        for user in self.users:
            if user["username"] == username and user["password_hash"] == self.hash_password(password):
                self.current_user = user
                return True
        return False
    
    def is_owner(self):
        #Verifica si el usuario actual es el dueño
        return self.current_user and self.current_user.get("is_owner", False)
    
    def add_user(self, username, password, is_admin=False):
        # Agrega un nuevo usuario
        # Verificar si el usuario ya existe
        if any(user["username"] == username for user in self.users):
            raise ValueError("El nombre de usuario ya existe")
        # Creación del Objeto Usuario
        new_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "password_hash": self.hash_password(password),
            "is_admin": is_admin,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.users.append(new_user)
        self.save_users()
    
    def remove_user(self, username):
        # Elimina un usuario
        if not self.is_owner():
            raise PermissionError("Solo el dueño puede eliminar usuarios")
        
        if username == self.current_user["username"]:
            raise ValueError("No puedes eliminarte a ti mismo")
        
        self.users = [user for user in self.users if user["username"] != username]
        self.save_users()
    
    def change_password(self, username, new_password):
        # Cambia la contraseña de un usuario
        if not self.is_owner() and username != self.current_user["username"]:
            raise PermissionError("Solo puedes cambiar tu propia contraseña")
        
        for user in self.users:
            if user["username"] == username:
                user["password_hash"] = self.hash_password(new_password)
                self.save_users()
                return True
        return False
    
    def get_all_users(self):
        # Obtiene todos los usuarios 
        return [{
            "username": user["username"],
            "is_admin": user.get("is_admin", False),
            "is_owner": user.get("is_owner", False)
        } for user in self.users]

class Inventario:
    # Es el sistema de gestión de stock de ingredientes
    def __init__(self):
        # Ingredientes predeterminados
        self.ingredientes = {
            "leche": {"cantidad": 100, "unidad": "ml"},
            "harina": {"cantidad": 100, "unidad": "gr"},
            "café": {"cantidad": 100, "unidad": "gr"},
            "chocolate": {"cantidad": 100, "unidad": "gr"},
            "azúcar": {"cantidad": 100, "unidad": "gr"},
            "huevos": {"cantidad": 100, "unidad": "unidades"},
            "agua": {"cantidad": 100, "unidad": "ml"}
        }
        self.ruta_inventario = os.path.join("D:", "DESCARGAS Y COSAS", "inventario.json")
        self.cargar_inventario() 
    
    def cargar_inventario(self):
        # Carga datos desde JSON o inicializa uno nuevo
        try:
            with open(self.ruta_inventario, 'r') as f:
                self.ingredientes = json.load(f)
        except FileNotFoundError:
            self.guardar_inventario()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "El archivo de inventario está corrupto. Se creará uno nuevo.")
            self.guardar_inventario()  
    
    def guardar_inventario(self):
        # Guarda el inventario actual en el archivo JSON
        try:
            with open(self.ruta_inventario, 'w') as f:
                json.dump(self.ingredientes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el inventario: {str(e)}")
    
    def verificar_disponibilidad(self, ingrediente, cantidad):
        # Control de stock
        return ingrediente in self.ingredientes and self.ingredientes[ingrediente]["cantidad"] >= cantidad
    
    def consumir_ingredientes(self, ingredientes):
        # Consume una cantidad de ingredientes del inventario
        for ingrediente, cantidad in ingredientes.items():
            if not self.verificar_disponibilidad(ingrediente, cantidad):
                raise ValueError(f"No hay suficiente {ingrediente}")
        
        for ingrediente, cantidad in ingredientes.items():
            self.ingredientes[ingrediente]["cantidad"] -= cantidad
        self.guardar_inventario()
    
    def agregar_ingrediente(self, ingrediente, cantidad):
        # Añade cantidad a un ingrediente existente y no permite crear nuevos ingredientes 
        if ingrediente in self.ingredientes:
            self.ingredientes[ingrediente]["cantidad"] += cantidad
        else:
            raise KeyError(f"Ingrediente {ingrediente} no existe")
        self.guardar_inventario()
    
    def actualizar_ingrediente(self, ingrediente, cantidad, unidad=None):
        if ingrediente in self.ingredientes:
            # Actualizacion existe
            self.ingredientes[ingrediente]["cantidad"] = cantidad
            if unidad:
                self.ingredientes[ingrediente]["unidad"] = unidad
        else:
            # Creacion nueva
            if not unidad:
                unidad = self._determinar_unidad_predeterminada(ingrediente)
            self.ingredientes[ingrediente] = {"cantidad": cantidad, "unidad": unidad}
        self.guardar_inventario()
    
    def eliminar_ingrediente(self, ingrediente):
        # Elimina un ingrediente del inventario
        if ingrediente in self.ingredientes:
            del self.ingredientes[ingrediente]
            self.guardar_inventario()
            return True
        return False
    
    def agregar_nuevo_ingrediente(self, nombre, cantidad, unidad):
        # Agrega un nuevo ingrediente al inventario
        if nombre in self.ingredientes:
            raise ValueError(f"Ingrediente {nombre} ya existe")
        
        if not unidad:
            unidad = self._determinar_unidad_predeterminada(nombre)
            
        self.ingredientes[nombre] = {
            "cantidad": cantidad,
            "unidad": unidad
        }
        self.guardar_inventario()
    
    def _determinar_unidad_predeterminada(self, ingrediente):
        # Líquidos se miden en mililitros
        if ingrediente in ["leche", "agua", "jugo"]:
            return "ml"
        # Ingredientes contables se miden por unidades
        elif ingrediente in ["huevos", "unidades", "piezas"]:
            return "unidades"
        # Por defecto, asumimos que son sólidos medidos en gramos
        return "gr"
    
    def obtener_estado(self):
        # Devuelve copia del inventario actual para evitar modificaciones directas
        return self.ingredientes.copy()
    
    def obtener_ingrediente(self, nombre):
        # Busca un ingrediente por nombre, retorna None si no existe
        return self.ingredientes.get(nombre, None)
    
    def reiniciar_inventario(self):
        # Restablece el inventario a valores iniciales y guarda los cambios
        self.ingredientes = {
            "leche": {"cantidad": 100, "unidad": "ml"},
            "harina": {"cantidad": 100, "unidad": "gr"},
            "café": {"cantidad": 100, "unidad": "gr"},
            "chocolate": {"cantidad": 100, "unidad": "gr"},
            "azúcar": {"cantidad": 100, "unidad": "gr"},
            "huevos": {"cantidad": 100, "unidad": "unidades"},
            "agua": {"cantidad": 100, "unidad": "ml"}
        }
        self.guardar_inventario()

class Producto:
    # Clase que representa un producto del menú de la cafetería
    def __init__(self, nombre, precio, categoria, imagen_path, ingredientes=None):
        # Inicializa un nuevo producto con sus características principales
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        self.imagen_path = imagen_path
        self.ingredientes = ingredientes or {}
    
    def __str__(self):
        # Representación legible del producto para mostrar al usuario
        return f"{self.nombre} (${self.precio:.2f})"

class CafeteriaApp:
    # Clase principal, que se encarga de gestionar la interfaz gráfica y la lógica de operación para usuarios, pedidos, inventario y productos de una cafetería.
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Cafetería")
        self.root.geometry("400x600")
        self.root.configure(bg="white")
        
        try:
            self.root.iconbitmap("D:/DESCARGAS Y COSAS/cafe.ico")  
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")  # Manejo de error si el archivo no existe

        self.user_manager = UserManager()
        self.inventario = Inventario()
        self.pedidos = []
        self.cargar_pedidos()
        self.cargar_productos()
        
        self.imagenes_tk = []
        self.mostrar_pantalla_inicio()

    def mostrar_pantalla_inicio(self):
        # Limpia la pantalla actual eliminando todos los widgets existentes
        self.limpiar_pantalla()
        
        # Crea un frame principal que actuará como contenedor para todos los demás elementos
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame especial para contener las imágenes, centrado en la pantalla
        images_frame = tk.Frame(main_frame, bg="white")
        images_frame.pack(pady=(0, 30))
        
        # Intenta cargar y mostrar la imagen de inicio
        try:
  
            # Imagen 
            img2_path = os.path.join("D:", "DESCARGAS Y COSAS", "imageninicio.png")  
            img2 = Image.open(img2_path)
            img2 = img2.resize((280, 360), Image.Resampling.LANCZOS)
            self.img2_tk = ImageTk.PhotoImage(img2)
            img2_label = tk.Label(images_frame, image=self.img2_tk, bg="white")
            img2_label.pack()
            
        except Exception as e:
            print(f"Error al cargar imágenes: {e}")
            # Si hay error, muestra un mensaje en lugar de las imágenes
            tk.Label(images_frame, text="Logotipos no disponibles", bg="#f5f5f5").pack()
        
        # Crea y muestra un texto indicativo 
        tk.Label(
            main_frame, 
            text="Ingresa como:", 
            font=("Arial", 10), 
            bg="white"
        ).pack(pady=(0, 5))

        # Crea un frame especial para contener los botones de opción
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack()

        # Define un estilo común para ambos botones
        button_style = {
            "width": 15, 
            "height": 2, 
            "font": ("Arial", 10, "bold"),
            "bg": "#DBB5B5",  
            "fg": "Black",
            "border": 0
        }

        # Crea y muestra los botones para ingresar como cliente y administrador
        tk.Button(
            buttons_frame, 
            text="Cliente  →", 
            command=self.iniciar_como_cliente,
            **button_style
        ).pack(pady=5)

        tk.Button(
            buttons_frame, 
            text="Administrador  →", 
            command=self.iniciar_como_admin,
            **button_style
        ).pack(pady=10)

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def iniciar_como_cliente(self):
        nombre_cliente = simpledialog.askstring("Registro", "Ingrese su nombre para el pedido:")
        if nombre_cliente:
            self.nombre_cliente = nombre_cliente 
            self.mostrar_interfaz_cliente(nombre_cliente)

    def iniciar_como_admin(self):
        if not self.user_manager.users:  # Si no hay usuarios, crear admin por defecto
            self.user_manager.create_default_admin()
        
        self.mostrar_login_admin()

    def mostrar_login_admin(self):
        self.limpiar_pantalla()
        
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Imagen de login
        try:
            login_img_path = os.path.join("D:", "DESCARGAS Y COSAS", "admin_login.png")
            login_img = Image.open(login_img_path)
            login_img = login_img.resize((200, 150), Image.Resampling.LANCZOS)
            self.login_img_tk = ImageTk.PhotoImage(login_img)
            tk.Label(main_frame, image=self.login_img_tk, bg="white").pack(pady=10)
        except Exception as e:
            print(f"Error al cargar imagen de login: {e}")
            tk.Label(main_frame, text="Acceso Administrativo", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        
        # Campos de login
        tk.Label(main_frame, text="Usuario:", bg="white").pack(pady=5)
        self.username_entry = tk.Entry(main_frame)
        self.username_entry.pack(pady=5)
        
        tk.Label(main_frame, text="Contraseña:", bg="white").pack(pady=5)
        self.password_entry = tk.Entry(main_frame, show="*")
        self.password_entry.pack(pady=5)
        
        # Botón de login
        tk.Button(
            main_frame, 
            text="Iniciar Sesión", 
            command=self.verificar_login_admin,
            bg="#DBB5B5", fg="black", font=("Arial", 10, "bold"), pady=5, width=15
        ).pack(pady=20)
        
        # Botón para volver
        tk.Button(
            main_frame, 
            text="Volver", 
            command=self.mostrar_pantalla_inicio,
            bg="#F1E5D1", fg="black", font=("Arial", 10), pady=3, width=10
        ).pack(pady=5)
    def verificar_login_admin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Usuario y contraseña son requeridos")
            return
        
        if self.user_manager.authenticate(username, password):
            self.mostrar_interfaz_admin()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def mostrar_interfaz_cliente(self, nombre_cliente):
        self.limpiar_pantalla()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Imagen de la ventana de cliente
        try:
            img_path = os.path.join("D:", "DESCARGAS Y COSAS", "cliente.png") 
            img = Image.open(img_path)
            img = img.resize((320, 300), Image.Resampling.LANCZOS) 
            self.cliente_header_img = ImageTk.PhotoImage(img)  # Guardar referencia como atributo
            
            img_label = tk.Label(main_frame, image=self.cliente_header_img, bg="white")
            img_label.pack(pady=(0, 50))  
        except Exception as e:
            print(f"Error al cargar imagen: {e}")
            tk.Label(main_frame, text="Bienvenido", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
        
        # Título con nombre del cliente
        tk.Label(
            main_frame, 
            text=f"Hola!, {nombre_cliente}", 
            font=("Arial", 16, "bold"), 
            bg="white"
        ).pack(pady=(0, 20))  

        # Frame para los botones
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack()

        button_style = {
            "width": 15, 
            "height": 2, 
            "font": ("Arial", 10, "bold"),
            "bg": "#DBB5B5",  
            "fg": "Black",
            "border": 0
        }

        # Botones
        tk.Button(
            buttons_frame, 
            text="Realizar Pedido", 
            command=self.realizar_pedido,
            **button_style
        ).pack(pady=10, fill=tk.X)

        tk.Button(
            buttons_frame, 
            text="Volver al Inicio", 
            command=self.mostrar_pantalla_inicio,
            **{**button_style, "bg": "#F1E5D1"}
        ).pack(pady=10, fill=tk.X)
        
    def mostrar_interfaz_admin(self):
        self.limpiar_pantalla()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Barra superior con info de usuario
        user_frame = tk.Frame(main_frame, bg="#f5f5f5", padx=10, pady=5)
        user_frame.pack(fill=tk.X, pady=(0, 20))
        
        current_user = self.user_manager.current_user["username"]
        is_owner = self.user_manager.is_owner()
        
        tk.Label(
            user_frame, 
            text=f"Hola!, {current_user} {'(Gerente)' if is_owner else ''}", 
            bg="#f5f5f5", 
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT)
        
        tk.Button(
            user_frame,
            text="Cerrar Sesión",
            command=self.mostrar_pantalla_inicio,
            bg="#F1E5D1",
            fg="black",
            font=("Arial", 8),
            padx=5
        ).pack(side=tk.RIGHT)
        
        if is_owner:
            tk.Button(
                user_frame,
                text="Gestionar Usu.",
                command=self.mostrar_gestion_usuarios,
                bg="#DBB5B5",
                fg="black",
                font=("Arial", 8),
                padx=5
            ).pack(side=tk.RIGHT, padx=5)
        

        #Imagen en la ventana de administracion
        try:
            admin_img_path = os.path.join("D:", "DESCARGAS Y COSAS", "administrador.png")  
            admin_img = Image.open(admin_img_path)
            admin_img = admin_img.resize((150, 190), Image.Resampling.LANCZOS) 
            self.admin_header_img = ImageTk.PhotoImage(admin_img)  # Guardar referencia
            
            img_label = tk.Label(main_frame, image=self.admin_header_img, bg="white")
            img_label.pack(pady=(0, 20))  
        except Exception as e:
            print(f"Error al cargar imagen de admin: {e}")
            tk.Label(main_frame, text="Panel de Administración", 
                    font=("Arial", 18, "bold"), bg="white").pack(pady=10)
        
        # Título
        tk.Label(
            main_frame, 
            text="Panel de Administración", 
            font=("Arial", 16, "bold"), 
            bg="white"
        ).pack(pady=(0, 10))

        # Frame para los botones
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack()

        button_style = {
            "width": 15, 
            "height": 2, 
            "font": ("Arial", 10, "bold"),
            "bg": "#DBB5B5",  
            "fg": "Black",
            "border": 0
        }

        # Botones administrativos
        admin_buttons = [
            ("Agregar Producto", self.agregar_producto),
            ("Ver Productos", self.mostrar_inventario_productos),
            ("Ver Inventario", self.ver_inventario),
            ("Historial de Ventas", self.mostrar_historial_ventas)
        ]

        for text, command in admin_buttons:
            bg_color = "#F1E5D1" if text == "Volver al Inicio" else "#DBB5B5"
            tk.Button(
                buttons_frame, 
                text=text, 
                command=command,
                **{**button_style, "bg": bg_color}
            ).pack(pady=5, fill=tk.X)
            
    def mostrar_gestion_usuarios(self):
        # Muestra la interfaz para gestionar usuarios
        dialog = tk.Toplevel(self.root)
        dialog.title("Gestión de Usuarios")
        dialog.geometry("600x400")
        
        main_frame = tk.Frame(dialog, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            main_frame, 
            text="Gestión de Usuarios Administradores", 
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Frame para la lista de usuarios
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar usuarios
        columns = ("Usuario", "Rol")
        tree = ttk.Treeview(
            list_frame,
            columns=columns,
            selectmode="browse"
        )

        tree.heading("#0", text="ID")
        tree.column("#0", width=0, stretch=tk.NO)  # Ocultar columna ID
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150 if col == "Usuario" else 100)
        
        # Insertar datos
        for i, user in enumerate(self.user_manager.get_all_users(), 1):
            rol = "Dueño" if user.get("is_owner") else "Admin" if user.get("is_admin") else "Usuario"
            tree.insert("", tk.END, text=str(i), values=(user["username"], rol))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Frame para botones de acción
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botones
        tk.Button(
            button_frame,
            text="Agregar Usuario",
            command=lambda: self.agregar_usuario_dialog(dialog),
            bg="#3C5B6F",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Eliminar Usuario",
            command=lambda: self.eliminar_usuario(tree, dialog),
            bg="#E98580",
            fg="black",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cambiar Contraseña",
            command=lambda: self.cambiar_password_dialog(tree, dialog),
            bg="#153448",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cerrar",
            command=dialog.destroy,
            bg="#443627",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.RIGHT, padx=5)

    def agregar_usuario_dialog(self, parent):
        # Muestra diálogo para agregar nuevo usuario
        dialog = tk.Toplevel(parent)
        dialog.title("Agregar Nuevo Usuario")
        dialog.geometry("300x300")
        #
        # Variables TKinter para almacenar los datos del formulario
        username_var = tk.StringVar()
        password_var = tk.StringVar()
        confirm_var = tk.StringVar()
        is_admin_var = tk.BooleanVar(value=True)
        
        # Campos del formulario
        tk.Label(dialog, text="Nombre de usuario:").pack(pady=5)
        tk.Entry(dialog, textvariable=username_var).pack(pady=5)
        
        tk.Label(dialog, text="Contraseña:").pack(pady=5)
        tk.Entry(dialog, textvariable=password_var, show="*").pack(pady=5)
        
        tk.Label(dialog, text="Confirmar contraseña:").pack(pady=5)
        tk.Entry(dialog, textvariable=confirm_var, show="*").pack(pady=5)
        
        tk.Checkbutton(
            dialog, 
            text="Es administrador", 
            variable=is_admin_var
        ).pack(pady=5)
        
        def confirmar():
            username = username_var.get().strip()
            password = password_var.get()
            confirm = confirm_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Usuario y contraseña son requeridos")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            try:
                self.user_manager.add_user(username, password, is_admin_var.get())
                messagebox.showinfo("Éxito", "Usuario agregado correctamente")
                dialog.destroy()
                parent.destroy()  
                self.mostrar_gestion_usuarios()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(
            dialog,
            text="Agregar",
            command=confirmar,
            bg="#DBB5B5",
            fg="black"
        ).pack(pady=10)

    def eliminar_usuario(self, tree, parent):
        # Elimina el usuario seleccionado
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
        
        item = seleccion[0]
        username = tree.item(item, "values")[0]
        
        try:
            self.user_manager.remove_user(username)
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            parent.destroy()  
            self.mostrar_gestion_usuarios()
        except (PermissionError, ValueError) as e:
            messagebox.showerror("Error", str(e))

    def cambiar_password_dialog(self, tree, parent):
        # Muestra diálogo para cambiar contraseña
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un usuario")
            return
        
        item = seleccion[0]
        username = tree.item(item, "values")[0]
        
        # Verificar permisos (dueño puede cambiar cualquier contraseña, otros solo la suya)
        current_user = self.user_manager.current_user["username"]
        if not self.user_manager.is_owner() and username != current_user:
            messagebox.showerror("Error", "Solo puedes cambiar tu propia contraseña")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("Cambiar Contraseña")
        dialog.geometry("300x200")
        
        # Variables
        new_pass_var = tk.StringVar()
        confirm_var = tk.StringVar()
        
        # Campos del formulario
        tk.Label(dialog, text=f"Cambiar contraseña para {username}").pack(pady=5)
        
        tk.Label(dialog, text="Nueva contraseña:").pack(pady=5)
        tk.Entry(dialog, textvariable=new_pass_var, show="*").pack(pady=5)
        
        tk.Label(dialog, text="Confirmar contraseña:").pack(pady=5)
        tk.Entry(dialog, textvariable=confirm_var, show="*").pack(pady=5)
        
        def confirmar():
            new_pass = new_pass_var.get()
            confirm = confirm_var.get()
            
            if not new_pass or not confirm:
                messagebox.showerror("Error", "Todos los campos son requeridos")
                return
            
            if new_pass != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return
            
            try:
                self.user_manager.change_password(username, new_pass)
                messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(
            dialog,
            text="Cambiar",
            command=confirmar,
            bg="#2196F3",
            fg="white"
        ).pack(pady=10)

    def cargar_pedidos(self):
        ruta_pedidos = os.path.join("D:", "DESCARGAS Y COSAS", "pedidos.json")
        try:
            with open(ruta_pedidos, 'r') as f:
                self.pedidos = json.load(f)
        except FileNotFoundError:
            self.pedidos = []
    
    def guardar_pedidos(self):
        ruta_pedidos = os.path.join("D:", "DESCARGAS Y COSAS", "pedidos.json")
        with open(ruta_pedidos, 'w') as f:
            json.dump(self.pedidos, f, indent=4)

    def cargar_productos(self):
        ruta_productos = os.path.join("D:", "DESCARGAS Y COSAS", "productos.json")
        try:
            with open(ruta_productos, 'r') as f:
                data = json.load(f)
                self.bebidas = [Producto(**p) for p in data.get('bebidas', [])]
                self.postres = [Producto(**p) for p in data.get('postres', [])]
        except FileNotFoundError:
            self.bebidas = [
                Producto("Expreso", 35.00, "Bebida", os.path.join("D:", "DESCARGAS Y COSAS", "espresso.png"), {"café": 10, "agua": 30}),
                Producto("Macchiato", 40.00, "Bebida", os.path.join("D:", "DESCARGAS Y COSAS", "macchiato.png"), {"café": 10, "leche": 100}),
                Producto("Chocolate", 35.00, "Bebida", os.path.join("D:", "DESCARGAS Y COSAS", "chocolate.png"), {"chocolate": 20, "leche": 100, "azúcar": 10}),
            ]
            self.postres = [
                Producto("Cupcake Celestial", 6.00, "Postre", os.path.join("D:", "DESCARGAS Y COSAS", "cupcake_celestial.png"), {"harina": 50, "huevos": 1, "azúcar": 20}),
                Producto("Pastel de Chocolate", 8.00, "Postre", os.path.join("D:", "DESCARGAS Y COSAS", "pastel_chocolate.png"), {"harina": 50, "huevos": 2, "chocolate": 30, "azúcar": 20}),
            ]
            self.guardar_productos()

    def guardar_productos(self):
        ruta_productos = os.path.join("D:", "DESCARGAS Y COSAS", "productos.json")
        data = {
            'bebidas': [{'nombre': p.nombre, 'precio': p.precio, 'categoria': p.categoria, 
                        'imagen_path': p.imagen_path, 'ingredientes': p.ingredientes} 
                        for p in self.bebidas],
            'postres': [{'nombre': p.nombre, 'precio': p.precio, 'categoria': p.categoria, 
                        'imagen_path': p.imagen_path, 'ingredientes': p.ingredientes} 
                        for p in self.postres]
        }
        with open(ruta_productos, 'w') as f:
            json.dump(data, f, indent=4)
    

    def realizar_pedido(self):
        # Crea una nueva ventana emergente para realizar pedidos
        self.pedido_window = tk.Toplevel(self.root)
        self.pedido_window.title("Realizar Pedido")
        self.pedido_window.geometry("1000x500")
        self.pedido_window.configure(bg="#f5f5f5")

        self.productos_seleccionados = []
        self.total_pedido = 0.0

        main_frame = tk.Frame(self.pedido_window, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        left_frame = tk.Frame(main_frame, bg="#f5f5f5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        notebook = ttk.Notebook(left_frame)
        bebidas_frame = ttk.Frame(notebook)
        notebook.add(bebidas_frame, text="Bebidas")
        postres_frame = ttk.Frame(notebook)
        notebook.add(postres_frame, text="Postres")
        notebook.pack(fill=tk.BOTH, expand=True)

        def setup_product_frame(parent, productos):
            canvas = tk.Canvas(parent, bg="#f5f5f5", highlightthickness=0)
            scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

            for i in range(3):
                scrollable_frame.grid_columnconfigure(i, weight=1, uniform="cols")

            for i, producto in enumerate(productos):
                frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief="solid", padx=10, pady=10, width=150, height=220)
                frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
                frame.grid_propagate(False)
                
                try:
                    img_path = producto.imagen_path
                    if not os.path.exists(img_path):
                        img_path = os.path.join("images", "default.png")
                        if not os.path.exists(img_path):
                            raise FileNotFoundError("Imagen no encontrada")
                    
                    imagen = Image.open(img_path).resize((120, 120), Image.Resampling.LANCZOS)
                    imagen_tk = ImageTk.PhotoImage(imagen)
                    self.imagenes_tk.append(imagen_tk)
                    
                    tk.Label(frame, image=imagen_tk, bg="white").pack(pady=5)
                    tk.Label(frame, text=producto.nombre, bg="white", font=("Arial", 10, "bold"), wraplength=120).pack()
                    tk.Label(frame, text=f"${producto.precio:.2f}", bg="white", font=("Arial", 10, "bold"), fg="#443627").pack(pady=5)
                    
                    tk.Button(
                        frame, 
                        text="Agregar", 
                        command=lambda p=producto: self.agregar_producto_pedido(p),
                        bg="#443627", fg="white", relief="flat", font=("Arial", 9), padx=15, pady=3
                    ).pack(pady=5, fill=tk.X)
                    
                except Exception as e:
                    print(f"Error al cargar la imagen: {e}")
                    tk.Label(frame, text="Imagen no disponible", bg="white").pack()

        setup_product_frame(bebidas_frame, self.bebidas)
        setup_product_frame(postres_frame, self.postres)

        right_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid", width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))

        tk.Label(right_frame, text="Productos seleccionados", bg="white", font=("Arial", 12, "bold"), pady=10).pack(fill=tk.X)

        selected_list_frame = tk.Frame(right_frame, bg="white")
        selected_list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        selected_canvas = tk.Canvas(selected_list_frame, bg="white", highlightthickness=0)
        selected_scroll = tk.Scrollbar(selected_list_frame, orient="vertical", command=selected_canvas.yview)
        self.selected_items_frame = tk.Frame(selected_canvas, bg="white")

        self.selected_items_frame.bind("<Configure>", lambda e: selected_canvas.configure(scrollregion=selected_canvas.bbox("all")))
        selected_canvas.create_window((0, 0), window=self.selected_items_frame, anchor="nw")
        selected_canvas.configure(yscrollcommand=selected_scroll.set)

        selected_scroll.pack(side="right", fill="y")
        selected_canvas.pack(side="left", fill="both", expand=True)

        self.total_label = tk.Label(right_frame, text="Total: $0.00", bg="white", font=("Arial", 12, "bold"), pady=10)
        self.total_label.pack(fill=tk.X)

        tk.Button(
            right_frame, 
            text="Realizar pedido", 
            command=lambda: self.finalizar_pedido(),
            bg="#443627", fg="white", font=("Arial", 12), relief="flat", padx=20, pady=10
        ).pack(fill=tk.X, padx=10, pady=20)

        self.actualizar_resumen()

    def agregar_producto_pedido(self, producto):
        try:
            # Primero se verifica si hay suficiente inventario para la preparacion del producto
            for ingrediente, cantidad in producto.ingredientes.items():
                if not self.inventario.verificar_disponibilidad(ingrediente, cantidad):
                    raise ValueError(f"No hay suficiente {ingrediente} para preparar {producto.nombre}")
            
            # Si pasa la verificación, consumimos los ingredientes y agregamos al pedido
            self.inventario.consumir_ingredientes(producto.ingredientes)
            self.productos_seleccionados.append(producto)
            self.total_pedido += producto.precio
            self.actualizar_resumen()
        except ValueError as e:
            # Se muestra el error pero se permite continuar
            messagebox.showerror("Producto no disponible", str(e))
            

    def actualizar_resumen(self):
        for widget in self.selected_items_frame.winfo_children():
            widget.destroy()

        for i, producto in enumerate(self.productos_seleccionados):
            item_frame = tk.Frame(self.selected_items_frame, bg="white", pady=5)
            item_frame.pack(fill=tk.X)
            
            tk.Label(item_frame, text=producto.nombre, bg="white", anchor="w", font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(item_frame, text=f"${producto.precio:.2f}", bg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=10)
            
            tk.Button(
                item_frame,
                text="✕",
                command=lambda idx=i: self.eliminar_producto(idx),
                bg="#DF5E5E", fg="white", font=("Arial", 8), relief="flat", width=2
            ).pack(side=tk.RIGHT)

        self.total_label.config(text=f"Total: ${self.total_pedido:.2f}")

    def eliminar_producto(self, index):
        producto = self.productos_seleccionados.pop(index)
        self.total_pedido -= producto.precio
        
        for ingrediente, cantidad in producto.ingredientes.items():
            self.inventario.agregar_ingrediente(ingrediente, cantidad)
        
        self.actualizar_resumen()

    def finalizar_pedido(self):
        # Verificar que hay productos seleccionados
        if not self.productos_seleccionados:
            messagebox.showwarning("Pedido vacío", "No has seleccionado ningún producto para tu pedido.")
            return

        try:
            # Crear registro del pedido
            resumen = {
                "cliente": self.nombre_cliente,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "productos": [p.nombre for p in self.productos_seleccionados],
                "cantidades": [1 for _ in self.productos_seleccionados],  # Puedes modificar esto si manejas cantidades
                "total": round(self.total_pedido, 2),
                "detalle": [f"{p.nombre} (${p.precio:.2f})" for p in self.productos_seleccionados]
            }

            # Agregar a la lista de pedidos
            self.pedidos.append(resumen)

            # Intentar guardar los pedidos
            try:
                self.guardar_pedidos()
            except Exception as e:
                # Si falla el guardado, revertir los cambios en el inventario
                for producto in self.productos_seleccionados:
                    for ingrediente, cantidad in producto.ingredientes.items():
                        self.inventario.agregar_ingrediente(ingrediente, cantidad)
                messagebox.showerror("Error", f"No se pudo guardar el pedido: {str(e)}")
                return

            # Mostrar confirmación detallada
            detalles_pedido = "\n".join([f"- {p.nombre}: ${p.precio:.2f}" for p in self.productos_seleccionados])
            
            respuesta = messagebox.askyesno(
                "Pedido Completado",
                f"¡Pedido registrado con éxito!\n\n"
                f"Cliente: {self.nombre_cliente}\n"
                f"Productos:\n{detalles_pedido}\n"
                f"Total: ${self.total_pedido:.2f}\n\n"
                f"¿Desea imprimir el ticket?",
                parent=self.pedido_window
            )

            if respuesta:
                # Aquí puedes agregar la lógica para imprimir el ticket
                messagebox.showinfo("Impresión", "Ticket enviado a la impresora", parent=self.pedido_window)

            # Cerrar ventana de pedido
            self.pedido_window.destroy()
            
            # Opcional: Mostrar mensaje de agradecimiento
            messagebox.showinfo("Gracias", "¡Gracias por tu compra! Vuelve pronto.", parent=self.root)

        except Exception as e:
            # Manejo de cualquier otro error inesperado
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {str(e)}", parent=self.pedido_window)
            # Intentar revertir cambios en inventario
            try:
                for producto in self.productos_seleccionados:
                    for ingrediente, cantidad in producto.ingredientes.items():
                        self.inventario.agregar_ingrediente(ingrediente, cantidad)
            except Exception as ex:
                messagebox.showerror("Error Crítico", f"No se pudieron revertir los cambios: {str(ex)}", parent=self.pedido_window)

    def agregar_producto(self):
        # Oculta la ventana principal (administrador)
        self.root.withdraw()  

        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Producto")
        dialog.geometry("500x600")

        # Configurar qué hacer al cerrar el diálogo
        def on_close():
            dialog.destroy()
            self.root.deiconify()  # <--- Restaura la ventana principal
            
        dialog.protocol("WM_DELETE_WINDOW", on_close)  # <--- Maneja el cierre
        
        # Variables para el nuevo producto
        nombre_var = tk.StringVar()
        precio_var = tk.StringVar()
        categoria_var = tk.StringVar(value="Bebida")
        imagen_var = tk.StringVar()
        
        # Diccionario para almacenar los ingredientes seleccionados
        self.ingredientes_seleccionados = {}
        
        # Frame principal con scroll
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Información básica del producto
        tk.Label(scrollable_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(scrollable_frame, textvariable=nombre_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(scrollable_frame, text="Precio:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(scrollable_frame, textvariable=precio_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(scrollable_frame, text="Categoría:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.OptionMenu(scrollable_frame, categoria_var, "Bebida", "Postre").grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(scrollable_frame, text="Imagen (nombre.extension):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(scrollable_frame, textvariable=imagen_var).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Sección de ingredientes
        tk.Label(scrollable_frame, text="Ingredientes:", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Frame para la lista de ingredientes disponibles
        ingredientes_frame = tk.Frame(scrollable_frame)
        ingredientes_frame.grid(row=5, column=0, columnspan=2, sticky="ew")
        
        # Encabezados de la tabla de ingredientes
        tk.Label(ingredientes_frame, text="Ingrediente", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(ingredientes_frame, text="Cantidad", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5)
        tk.Label(ingredientes_frame, text="Unidad", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        
        # Crea un diccionario para mantener referencia a los Entry widgets
        self.entry_ingredientes = {}
        
        # Mostra todos los ingredientes disponibles
        for i, (ingrediente, datos) in enumerate(self.inventario.obtener_estado().items(), 1):
            tk.Label(ingredientes_frame, text=ingrediente).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            # Crea un Entry para cada ingrediente
            entry_cantidad = tk.Entry(ingredientes_frame, width=8)
            entry_cantidad.grid(row=i, column=1, padx=5, pady=2)
            self.entry_ingredientes[ingrediente] = entry_cantidad  # Guardamos referencia
            
            tk.Label(ingredientes_frame, text=datos['unidad']).grid(row=i, column=2, padx=5, pady=2)
            
            # Botón para agregar cada ingrediente (usa lambda con ingrediente y entry específicos)
            tk.Button(
                ingredientes_frame,
                text="Agregar",
                command=lambda ing=ingrediente, entry=entry_cantidad: self.agregar_ingrediente_producto(ing, entry),
                bg="#DBB5B5",
                fg="black",
                font=("Arial", 8)
            ).grid(row=i, column=3, padx=5, pady=2)
        
        # Frame para ingredientes seleccionados
        seleccionados_frame = tk.Frame(scrollable_frame)
        seleccionados_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
        
        tk.Label(seleccionados_frame, text="Ingredientes seleccionados:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.lista_seleccionados = tk.Listbox(seleccionados_frame, height=4)
        self.lista_seleccionados.pack(fill=tk.X, pady=5)
        
        def eliminar_seleccionado():
            seleccion = self.lista_seleccionados.curselection()
            if seleccion:
                ingrediente = self.lista_seleccionados.get(seleccion[0]).split(":")[0].strip()
                del self.ingredientes_seleccionados[ingrediente]
                self.actualizar_lista_seleccionados()
        
        tk.Button(
            seleccionados_frame,
            text="Eliminar seleccionado",
            command=eliminar_seleccionado,
            bg="#F1E5D1",
            fg="black",
            font=("Arial", 8)
        ).pack(pady=5)
        
        # Botón para confirmar
        tk.Button(
            scrollable_frame,
            text="Agregar Producto",
            command=lambda: [self.confirmar_agregar_producto(nombre_var, precio_var, categoria_var, imagen_var, dialog),on_close()],
            bg="#443627",
            fg="white",
            font=("Arial", 10, "bold"),
            pady=10
        ).grid(row=7, column=0, columnspan=2, pady=20, sticky="ew")
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def agregar_ingrediente_producto(self, ingrediente, entry_cantidad):
        cantidad = entry_cantidad.get()
        if cantidad:
            try:
                cantidad_float = float(cantidad)
                if cantidad_float <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser mayor que cero")
                    return
                    
                self.ingredientes_seleccionados[ingrediente] = cantidad_float
                entry_cantidad.delete(0, tk.END)
                self.actualizar_lista_seleccionados()
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número válido")

    def actualizar_lista_seleccionados(self):
        self.lista_seleccionados.delete(0, tk.END)
        for ingrediente, cantidad in self.ingredientes_seleccionados.items():
            unidad = self.inventario.obtener_ingrediente(ingrediente)['unidad']
            self.lista_seleccionados.insert(tk.END, f"{ingrediente}: {cantidad} {unidad}")

    def confirmar_agregar_producto(self, nombre_var, precio_var, categoria_var, imagen_var, dialog):
        try:
            nombre = nombre_var.get().strip()
            if not nombre:
                raise ValueError("El nombre no puede estar vacío")
            
            precio = float(precio_var.get())
            if precio <= 0:
                raise ValueError("El precio debe ser mayor que cero")
            
            categoria = categoria_var.get()
            imagen_nombre = imagen_var.get().strip()
            
            if not self.ingredientes_seleccionados:
                raise ValueError("Debe seleccionar al menos un ingrediente")
            
            # Modificado para usar la ruta especificada
            imagen_path = os.path.join("D:", "DESCARGAS Y COSAS", imagen_nombre)
            
            nuevo_producto = Producto(nombre, precio, categoria, imagen_path, self.ingredientes_seleccionados.copy())
            
            if categoria == "Bebida":
                self.bebidas.append(nuevo_producto)
            else:
                self.postres.append(nuevo_producto)
            
            self.guardar_productos()
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
##
    def mostrar_inventario_productos(self):
        """Muestra una ventana con la lista de productos existentes para editar/eliminar"""
        # Cerrar la ventana actual de gestión
        self.root.withdraw()

        # Crear nueva ventana para el inventario
        self.inventario_window = tk.Toplevel()
        self.inventario_window.title("Inventario de Productos")
        self.inventario_window.geometry("1000x600")
        
        # Configurar qué hacer al cerrar esta ventana
        def on_close():
            self.inventario_window.destroy()
            self.root.deiconify()
        
        self.inventario_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # Frame principal que contendrá todas las vistas
        self.main_container = tk.Frame(self.inventario_window)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mostrar la vista de lista inicialmente
        self.mostrar_lista_productos()

    def mostrar_lista_productos(self):
        """Muestra la lista de productos en el contenedor principal"""
        # Limpiar el contenedor principal
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Notebook para categorías
        notebook = ttk.Notebook(self.main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña para Bebidas
        bebidas_frame = ttk.Frame(notebook)
        notebook.add(bebidas_frame, text="Bebidas")
        self._crear_tabla_productos(bebidas_frame, self.bebidas)
        
        # Pestaña para Postres
        postres_frame = ttk.Frame(notebook)
        notebook.add(postres_frame, text="Postres")
        self._crear_tabla_productos(postres_frame, self.postres)
        
        # Botón para cerrar 
        tk.Button(
            self.main_container,
            text="Cerrar",
            command=lambda: [self.inventario_window.destroy(), self.root.deiconify()], 
            bg="#443627",
            fg="white",
            font=("Arial", 10, "bold"),
            pady=5
        ).pack(pady=10)

    def _crear_tabla_productos(self, parent, productos):
        """Crea la tabla de productos con opciones de editar/eliminar"""
        # Frame para la tabla
        table_frame = tk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        scroll_y = tk.Scrollbar(table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("Nombre", "Precio", "Ingredientes")
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode="browse"
        )
        
        # Configurar columnas
        tree.heading("#0", text="ID")
        tree.column("#0", width=50, stretch=tk.NO)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200 if col == "Ingredientes" else 100)
        
        # Insertar datos
        for i, producto in enumerate(productos, 1):
            ingredientes = ", ".join([f"{k}:{v}" for k, v in producto.ingredientes.items()])
            tree.insert("", tk.END, text=str(i), 
                    values=(producto.nombre, f"${producto.precio:.2f}", ingredientes))
        
        tree.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        
        # Frame para botones de acción
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones
        tk.Button(
            button_frame,
            text="Editar Producto",
            command=lambda: self._mostrar_formulario_edicion(tree, productos),
            bg="#DBB5B5",
            fg="black",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Eliminar Producto",
            command=lambda: self._eliminar_producto(tree, productos),
            bg="#E98580",
            fg="black",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        # Configurar doble clic para editar
        tree.bind("<Double-1>", lambda e: self._mostrar_formulario_edicion(tree, productos))

    def _mostrar_formulario_edicion(self, tree, productos):
        """Muestra el formulario de edición en el mismo contenedor"""
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para editar")
            return
        
        item = seleccion[0]
        idx = int(tree.index(item))
        self.producto_actual = productos[idx]
        
        # Limpiar el contenedor principal
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Frame principal del formulario
        form_frame = tk.Frame(self.main_container)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(
            form_frame, 
            text=f"Editando: {self.producto_actual.nombre}",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Campos del formulario
        campos_frame = tk.Frame(form_frame)
        campos_frame.pack(fill=tk.X, pady=10)
        
        # Nombre
        tk.Label(campos_frame, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        nombre_entry = tk.Entry(campos_frame)
        nombre_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        nombre_entry.insert(0, self.producto_actual.nombre)
        
        # Precio
        tk.Label(campos_frame, text="Precio:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        precio_entry = tk.Entry(campos_frame)
        precio_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        precio_entry.insert(0, str(self.producto_actual.precio))
        
        # Categoría
        tk.Label(campos_frame, text="Categoría:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        categoria_var = tk.StringVar(value=self.producto_actual.categoria)
        tk.OptionMenu(campos_frame, categoria_var, "Bebida", "Postre").grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Frame para ingredientes
        ingredientes_frame = tk.LabelFrame(form_frame, text="Ingredientes", padx=5, pady=5)
        ingredientes_frame.pack(fill=tk.X, pady=10)
        
        # Lista de ingredientes
        self.ingredientes_entries = {}
        for i, (ingrediente, cantidad) in enumerate(self.producto_actual.ingredientes.items()):
            tk.Label(ingredientes_frame, text=f"{ingrediente}:").grid(row=i, column=0, sticky="e", padx=5)
            entry = tk.Entry(ingredientes_frame, width=10)
            entry.grid(row=i, column=1, sticky="w", padx=5)
            entry.insert(0, str(cantidad))
            tk.Label(ingredientes_frame, text=self.inventario.obtener_ingrediente(ingrediente)['unidad']).grid(row=i, column=2, sticky="w", padx=5)
            self.ingredientes_entries[ingrediente] = entry
        
        # Botones
        button_frame = tk.Frame(form_frame)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Guardar Cambios",
            command=lambda: self._guardar_cambios_producto(
                nombre_entry.get(),
                precio_entry.get(),
                categoria_var.get()
            ),
            bg="#DBB5B5",
            fg="Black"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.mostrar_lista_productos,
            bg="#DF5E5E",
            fg="Black"
        ).pack(side=tk.LEFT, padx=5)

    def _guardar_cambios_producto(self, nombre, precio, categoria):
        """Guarda los cambios del producto y vuelve a la lista"""
        try:
            # Validar datos
            if not nombre.strip():
                raise ValueError("El nombre no puede estar vacío")
            
            precio = float(precio)
            if precio <= 0:
                raise ValueError("El precio debe ser mayor que cero")
            
            # Actualizar producto
            self.producto_actual.nombre = nombre.strip()
            self.producto_actual.precio = precio
            self.producto_actual.categoria = categoria
            
            # Actualizar ingredientes
            for ingrediente, entry in self.ingredientes_entries.items():
                cantidad = float(entry.get())
                self.producto_actual.ingredientes[ingrediente] = cantidad
            
            # Guardar cambios
            self.guardar_productos()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            self.mostrar_lista_productos()
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")

    def _eliminar_producto(self, tree, productos):
        """Elimina el producto seleccionado"""
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un producto para eliminar")
            return
        
        item = seleccion[0]
        idx = int(tree.index(item))
        producto = productos[idx]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar el producto {producto.nombre}?"):
            productos.pop(idx)
            self.guardar_productos()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            self.mostrar_lista_productos()


    def ver_inventario(self):
        # Verificar si ya existe una ventana de inventario
        if hasattr(self, 'inventario_window') and self.inventario_window.winfo_exists():
            # Limpiar el contenido existente excepto el frame principal
            for widget in self.inventario_window.winfo_children():
                widget.destroy()
            window = self.inventario_window
        else:
            # Si no existe, crear nueva ventana
            self.root.withdraw()
            window = tk.Toplevel(self.root)
            self.inventario_window = window
            window.title("Gestión de Inventario")
            window.geometry("600x600")

        # Función para manejar el cierre (siempre se recrea)
        def on_close():
            window.destroy()
            self.root.deiconify()
        
        window.protocol("WM_DELETE_WINDOW", on_close)

        # Frame principal
        main_frame = tk.Frame(window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para agregar nuevo ingrediente
        add_frame = tk.Frame(main_frame)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            add_frame,
            text="+ Agregar Nuevo Ingrediente",
            command=self.agregar_nuevo_ingrediente_dialog,
            bg="#443627",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(fill=tk.X)
        
        # Frame para la lista de inventario
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuración del scroll y canvas
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Encabezados
        tk.Label(scrollable_frame, text="Ingrediente", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(scrollable_frame, text="Cantidad", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(scrollable_frame, text="Unidad", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(scrollable_frame, text="Acciones", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=5)
        
        # Filas de ingredientes
        for i, (ingrediente, datos) in enumerate(self.inventario.obtener_estado().items(), 1):
            tk.Label(scrollable_frame, text=ingrediente, font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            cantidad_var = tk.StringVar(value=str(datos['cantidad']))
            tk.Entry(scrollable_frame, textvariable=cantidad_var, width=10, font=("Arial", 10)).grid(row=i, column=1, padx=5, pady=2)
            
            tk.Label(scrollable_frame, text=datos['unidad'], font=("Arial", 10)).grid(row=i, column=2, padx=5, pady=2)
            
            action_frame = tk.Frame(scrollable_frame)
            action_frame.grid(row=i, column=3, padx=5, pady=2)
            
            tk.Button(
                action_frame,
                text="Actualizar",
                command=lambda ing=ingrediente, var=cantidad_var: self.actualizar_cantidad(ing, var),
                bg="#DBB5B5",
                fg="black",
                font=("Arial", 8, "bold"),
                width=8
            ).pack(side=tk.LEFT, padx=2)
            
            tk.Button(
                action_frame,
                text="Eliminar",
                command=lambda ing=ingrediente: self.eliminar_ingrediente(ing, window),
                bg="#F1E5D1",
                fg="black",
                font=("Arial", 8, "bold"),
                width=8
            ).pack(side=tk.LEFT, padx=2)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón Cerrar (siempre se recrea)
        tk.Button(
            main_frame,
            text="Cerrar",
            command=on_close,
            bg="#443627",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15
        ).pack(pady=10)
        
        # Traer al frente si ya existía
        if hasattr(self, 'inventario_window'):
            window.lift()
#
    def agregar_nuevo_ingrediente_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Nuevo Ingrediente")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        nombre_entry = tk.Entry(dialog)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        cantidad_entry = tk.Entry(dialog)
        cantidad_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Unidad:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        unidad_var = tk.StringVar(value="gr")
        tk.OptionMenu(dialog, unidad_var, "gr", "ml", "unidades").grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        def confirmar():
            try:
                nombre = nombre_entry.get().strip()
                cantidad = float(cantidad_entry.get())
                unidad = unidad_var.get()
                
                if not nombre:
                    raise ValueError("El nombre no puede estar vacío")
                
                self.inventario.agregar_nuevo_ingrediente(nombre, cantidad, unidad)
                messagebox.showinfo("Éxito", "Ingrediente agregado correctamente")
                dialog.destroy()
                self.ver_inventario()  # Refrescar la vista
            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        
        tk.Button(
            dialog,
            text="Agregar",
            command=confirmar,
            bg="#DBB5B5",
            fg="white"
        ).grid(row=3, columnspan=2, pady=10)

    def actualizar_cantidad(self, ingrediente, cantidad_var):
        try:
            nueva_cantidad = float(cantidad_var.get())
            self.inventario.actualizar_ingrediente(ingrediente, nueva_cantidad)
            messagebox.showinfo("Éxito", f"Cantidad de {ingrediente} actualizada")
        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")

    def eliminar_ingrediente(self, ingrediente, parent_window):
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar {ingrediente} del inventario?"):
            try:
                del self.inventario.ingredientes[ingrediente]
                self.inventario.guardar_inventario()
                messagebox.showinfo("Éxito", f"Ingrediente {ingrediente} eliminado")
                parent_window.destroy()
                self.ver_inventario()  # Refrescar la vista
            except KeyError:
                messagebox.showerror("Error", f"No se encontró el ingrediente {ingrediente}")

    def mostrar_historial_ventas(self):
        # Oculta la ventana principal (administrador)
        self.root.withdraw()  # <--- Oculta la ventana principal

        dialog = tk.Toplevel(self.root)
        dialog.title("Historial de Ventas")
        dialog.geometry("900x650")

        # Función para manejar el cierre de la ventana
        def on_close():
            dialog.destroy()
            self.root.deiconify()  # <--- Restaura la ventana principal
        
        dialog.protocol("WM_DELETE_WINDOW", on_close)  # <--- Configurar acción al cerrar
    
        
        # Frame principal
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para los botones de acción
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón para limpiar historial
        tk.Button(buttons_frame,
                text="Limpiar Historial",
                command=self.limpiar_historial,
                bg="#DF5E5E",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=15).pack(side=tk.LEFT, padx=5)
        
        # Botón para actualizar
        tk.Button(buttons_frame,
                text="Actualizar",
                command=lambda: self.actualizar_historial(tree),
                bg="#3C5B6F",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=15).pack(side=tk.LEFT, padx=5)
        
        # Botón para cerrar
        tk.Button(buttons_frame,
                text="Cerrar",
                command=on_close,
                bg="#443627",
                fg="white",
                font=("Arial", 10, "bold"),
                padx=15).pack(side=tk.RIGHT, padx=5)
        
        # Frame para el Treeview
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para mostrar los pedidos
        tree = ttk.Treeview(tree_frame, 
                        columns=("Fecha", "Cliente", "Productos", "Total"), 
                        yscrollcommand=scrollbar.set,
                        selectmode="extended")
        
        # Configurar columnas
        tree.heading("#0", text="ID", anchor=tk.W)
        tree.heading("Fecha", text="Fecha", anchor=tk.W)
        tree.heading("Cliente", text="Cliente", anchor=tk.W)
        tree.heading("Productos", text="Productos", anchor=tk.W)
        tree.heading("Total", text="Total", anchor=tk.W)
        
        tree.column("#0", width=50, stretch=tk.NO)
        tree.column("Fecha", width=150, stretch=tk.NO)
        tree.column("Cliente", width=150)
        tree.column("Productos", width=300)
        tree.column("Total", width=100, stretch=tk.NO)
        
        # Insertar datos
        for i, pedido in enumerate(self.pedidos, 1):
            productos = ", ".join(pedido["productos"])
            tree.insert("", tk.END, text=str(i), 
                    values=(pedido["fecha"], pedido["cliente"], productos, f"${pedido['total']:.2f}"))
        
        tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)
        
        # Configurar estilo
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Añadir doble clic para ver detalles
        tree.bind("<Double-1>", lambda event: self.mostrar_detalle_pedido(tree, event))

    def limpiar_historial(self):
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea limpiar todo el historial de ventas?\nEsta acción no se puede deshacer."):
            self.pedidos = []
            try:
                self.guardar_pedidos()
                messagebox.showinfo("Éxito", "Historial de ventas limpiado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo limpiar el historial: {str(e)}")

    def actualizar_historial(self, tree):
        # Limpiar el treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Recargar pedidos
        self.cargar_pedidos()
        
        # Insertar datos actualizados
        for i, pedido in enumerate(self.pedidos, 1):
            productos = ", ".join(pedido["productos"])
            tree.insert("", tk.END, text=str(i), 
                    values=(pedido["fecha"], pedido["cliente"], productos, f"${pedido['total']:.2f}"))
        
        messagebox.showinfo("Actualizado", "Historial de ventas actualizado correctamente")

    def mostrar_detalle_pedido(self, tree, event):
        item = tree.selection()[0]
        valores = tree.item(item, 'values')
        
        # Buscar el pedido completo
        pedido = next((p for p in self.pedidos if p['fecha'] == valores[0] and p['cliente'] == valores[1]), None)
        
        if pedido:
            detalles = "\n".join(pedido["detalle"])
            messagebox.showinfo(
                "Detalle del Pedido",
                f"Cliente: {pedido['cliente']}\n"
                f"Fecha: {pedido['fecha']}\n"
                f"Productos:\n{detalles}\n"
                f"Total: ${pedido['total']:.2f}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    splash = SplashScreen(root, CafeteriaApp)
    root.mainloop()