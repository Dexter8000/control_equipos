from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

# Obtén la ruta absoluta al directorio 'data'
# Esto asume que este script se ejecuta desde la raíz del proyecto o desde la carpeta routers
# Puede que necesites ajustar la ruta si la estructura de ejecución es diferente.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Definimos la ruta al archivo de departamentos
DEPARTAMENTOS_FILE = os.path.join(DATA_DIR, 'departamentos.json')


# Endpoint para obtener los datos de departamentos
@router.get("/data/departamentos") # La ruta para acceder a estos datos será /data/departamentos
async def get_departamentos_data():
    """Lee y devuelve el contenido del archivo data/departamentos.json"""

    # Verificamos si el archivo existe
    if not os.path.exists(DEPARTAMENTOS_FILE):
        # Si el archivo no existe, devolvemos un error 404 Not Found
        raise HTTPException(status_code=404, detail="Archivo de departamentos no encontrado")

    try:
        # Intentamos abrir y leer el archivo JSON
        with open(DEPARTAMENTOS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Si la lectura es exitosa, devolvemos los datos (FastAPI los serializará a JSON)
        return data
    except json.JSONDecodeError:
        # Si hay un error al parsear el JSON del archivo
        raise HTTPException(status_code=500, detail="Error al decodificar el JSON del archivo de departamentos")
    except Exception as e:
        # Capturamos cualquier otro error que pueda ocurrir al leer el archivo
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al leer el archivo: {e}")