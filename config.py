import os
import json

# ============
# RUTAS BASE
# ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# ===========================
# FUNCIONES DE UTILIDAD JSON
# ===========================

def cargar_json(nombre_archivo):
    """
    Carga un archivo JSON desde la carpeta 'data'.
    Retorna una lista o diccionario según el contenido.
    """
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return []
    with open(ruta, 'r', encoding='utf-8') as file:
        return json.load(file)

def guardar_json(nombre_archivo, datos):
    """
    Guarda un diccionario o lista como JSON en la carpeta 'data'.
    """
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    with open(ruta, 'w', encoding='utf-8') as file:
        json.dump(datos, file, ensure_ascii=False, indent=4)
