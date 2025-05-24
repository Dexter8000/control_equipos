import json
import os

# --- Configuración de la ruta de la carpeta 'data' ---

# Obtener la ruta absoluta al directorio que contiene este script (json_db.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta al directorio 'data'.
# Esto asume que la carpeta 'data' está al mismo nivel que json_db.py (es decir, en la raíz del proyecto).
DATA_DIR = os.path.join(current_dir, 'data')

# Asegurarse de que el directorio 'data' existe.
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"DEBUG (json_db): Directorio 'data' creado en: {DATA_DIR}")
else:
    print(f"DEBUG (json_db): Directorio 'data' ya existe en: {DATA_DIR}")

# --- Funciones Genéricas para Cargar y Guardar JSON ---

def _get_filepath(filename):
    """
    Función auxiliar para obtener la ruta completa a un archivo JSON
    dentro del directorio 'data'.
    """
    return os.path.join(DATA_DIR, filename)

def cargar_json(filename, default_content=None):
    """
    Lee datos de un archivo JSON específico en la carpeta 'data'.
    Retorna el contenido del JSON. Si el archivo no existe o está vacío,
    devuelve default_content (por defecto, una lista vacía).
    """
    filepath = _get_filepath(filename)
    if default_content is None:
        default_content = [] # La mayoría de tus JSON son listas

    if not os.path.exists(filepath) or os.stat(filepath).st_size == 0:
        print(f"DEBUG (cargar_json): Archivo '{filename}' no encontrado o vacío. Retornando contenido por defecto.")
        return default_content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"DEBUG (cargar_json): Archivo '{filename}' cargado exitosamente. Contiene {len(data)} elementos." if isinstance(data, list) else f"DEBUG (cargar_json): Archivo '{filename}' cargado exitosamente.")
        return data
    except json.JSONDecodeError as e:
        print(f"ERROR (cargar_json): Error al decodificar JSON de '{filepath}': {e}. El archivo podría estar corrupto. Retornando contenido por defecto.")
        return default_content
    except Exception as e:
        print(f"ERROR (cargar_json): Ocurrió un error inesperado al cargar '{filepath}': {e}. Retornando contenido por defecto.")
        return default_content

def guardar_json(filename, data):
    """
    Guarda datos en un archivo JSON específico en la carpeta 'data'.
    """
    filepath = _get_filepath(filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"DEBUG (guardar_json): Datos guardados exitosamente en '{filename}'.")
        return True
    except Exception as e:
        print(f"ERROR (guardar_json): Error al guardar en '{filepath}': {e}")
        return False

# --- Funciones específicas para cada tipo de dato ---

def get_usuarios():
    """Carga los datos de usuarios desde usuarios.json."""
    return cargar_json("usuarios.json")

def save_usuarios(usuarios_data):
    """Guarda los datos de usuarios en usuarios.json."""
    return guardar_json("usuarios.json", usuarios_data)

def get_prestamos():
    """Carga los datos de préstamos desde prestamos.json."""
    return cargar_json("prestamos.json")

def save_prestamos(prestamos_data):
    """Guarda los datos de préstamos en prestamos.json."""
    return guardar_json("prestamos.json", prestamos_data)

# --- Inicialización de archivos JSON al arrancar ---
def initialize_json_files():
    """
    Verifica si los archivos JSON necesarios existen y los inicializa si no.
    """
    files_to_initialize = [
        'equipos.json',
        'auditoria.json',
        'categorias.json',
        'detalles_prestamo.json',
        'devoluciones.json',
        'prestamos.json', # <--- Asegúrate de que 'prestamos.json' esté en esta lista
        'subcategorias.json',
        'subtipos_prestamo.json',
        'tipos_prestamo.json',
        'usuarios.json',
        'trabajadores.json', # Si tienes un archivo trabajadores.json
        'departamentos.json', # Si tienes un archivo departamentos.json
        'configuracion.json', # Este suele ser un diccionario, no una lista
    ]

    print(f"DEBUG (initialize_json_files): Iniciando la verificación/creación de archivos JSON.")
    for filename in files_to_initialize:
        filepath = _get_filepath(filename)
        # También verifica si el archivo está vacío
        if not os.path.exists(filepath) or os.stat(filepath).st_size == 0:
            initial_content = [] # Por defecto, la mayoría de tus JSON son listas de objetos
            if filename == 'configuracion.json':
                initial_content = {} # La configuración suele ser un diccionario

            # Usamos la función genérica guardar_json para inicializar
            guardar_json(filename, initial_content)
            print(f"DEBUG (initialize_json_files): Archivo '{filename}' inicializado en '{filepath}' con contenido {type(initial_content).__name__} vacío.")
        else:
            print(f"DEBUG (initialize_json_files): Archivo '{filename}' ya existe y no está vacío.")

# IMPORTANTE: Para que initialize_json_files se ejecute al inicio,
# debes llamarla en tu `main.py` después de importar `json_db`.
# Esto se suele hacer al inicio de `main.py` o dentro de un evento de startup de FastAPI.
