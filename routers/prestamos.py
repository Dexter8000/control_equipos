# routers/prestamos.py

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import uuid # Para generar IDs únicos

# Importar las funciones de json_db
from json_db import (
    cargar_json,
    guardar_json,
    get_prestamos, # Nueva función específica para préstamos
    save_prestamos # Nueva función específica para préstamos
)
# Importar validar_token para proteger rutas que requieren autenticación
from routers.auth import validar_token

router = APIRouter()
templates = Jinja2Templates(directory="templates") # Asegúrate de que esto esté definido si lo usas para HTMLResponse

# ===========================
# Rutas para obtener datos (usando cargar_json de json_db)
# ===========================

@router.get("/usuarios_data", response_class=JSONResponse) # Renombrada para evitar conflicto si tienes router de usuarios
async def obtener_usuarios_data():
    return cargar_json("usuarios.json")

@router.get("/buscar_persona/{placa}", response_class=JSONResponse)
async def buscar_persona(placa: str):
    trabajadores = cargar_json("Trabajadores.json") # Asegúrate de que el nombre del archivo sea "Trabajadores.json" o "trabajadores.json"
    persona = next((p for p in trabajadores if p["placa"] == placa), None)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    departamentos = cargar_json("departamentos.json")
    departamento = next((d for d in departamentos if d["id"] == persona.get("departamento_id")), None)
    persona["nombre_departamento"] = departamento["nombre"] if departamento else "Desconocido"
    return persona

@router.get("/tipos_prestamo", response_class=JSONResponse)
async def obtener_tipos_prestamo():
    return cargar_json("tipos_prestamo.json")

@router.get("/subtipos_prestamo/{tipo_prestamo_id}", response_class=JSONResponse)
async def obtener_subtipos_prestamo(tipo_prestamo_id: str):
    subtipos = [
        s for s in cargar_json("subtipos_prestamo.json")
        if str(s["tipo_prestamo_id"]) == tipo_prestamo_id # Asegúrate de que la comparación sea de tipo string
    ]
    if not subtipos:
        # Se devuelve 200 con lista vacía si no hay subtipos, no 404 a menos que el ID sea inválido
        # o que no existan subtipos para ese ID (pero la lista vacía es más amigable).
        return []
    return subtipos

@router.post("/agregar_tipo_prestamo", response_class=JSONResponse)
async def agregar_tipo_prestamo(tipo: dict):
    nuevo_nombre_tipo = tipo.get("nombre")
    if not nuevo_nombre_tipo:
        raise HTTPException(status_code=400, detail="Nombre del tipo de préstamo inválido")

    tipos = cargar_json("tipos_prestamo.json")
    if any(t.get("nombre") == nuevo_nombre_tipo for t in tipos):
        raise HTTPException(status_code=400, detail="Tipo de préstamo ya existe")
    
    # Generar un ID único (o incremental si prefieres, pero UUID es más robusto)
    nuevo_id = str(uuid.uuid4()) # Usando UUID para IDs únicos
    # Si quieres incremental, tendrías que convertir los IDs a int y encontrar el max.
    # nuevo_id = max((t["id"] for t in tipos if isinstance(t.get("id"), int)), default=0) + 1 
    
    tipos.append({"id": nuevo_id, "nombre": nuevo_nombre_tipo})
    
    if guardar_json("tipos_prestamo.json", tipos):
        return JSONResponse(status_code=201, content={"mensaje": f"Tipo '{nuevo_nombre_tipo}' agregado", "id": nuevo_id})
    raise HTTPException(status_code=500, detail="Fallo al guardar el tipo de préstamo")

@router.post("/agregar_subtipo_prestamo", response_class=JSONResponse)
async def agregar_subtipo_prestamo(subtipo: dict):
    tipo_prestamo_id = subtipo.get("tipo_prestamo_id")
    nuevo_nombre_subtipo = subtipo.get("nombre")
    
    if not tipo_prestamo_id or not nuevo_nombre_subtipo:
        raise HTTPException(status_code=400, detail="Datos incompletos para agregar subtipo")

    subtipos = cargar_json("subtipos_prestamo.json")
    if any(str(s.get("tipo_prestamo_id")) == tipo_prestamo_id and s.get("nombre") == nuevo_nombre_subtipo for s in subtipos):
        raise HTTPException(status_code=400, detail="Subtipo ya existe para este tipo de préstamo")
    
    # Generar un ID único
    nuevo_id = str(uuid.uuid4()) # Usando UUID para IDs únicos
    # Si quieres incremental:
    # nuevo_id = max((s["id"] for s in subtipos if isinstance(s.get("id"), int)), default=0) + 1 

    subtipos.append({
        "id": nuevo_id,
        "tipo_prestamo_id": tipo_prestamo_id,
        "nombre": nuevo_nombre_subtipo
    })
    
    if guardar_json("subtipos_prestamo.json", subtipos):
        return JSONResponse(status_code=201, content={"mensaje": f"Subtipo '{nuevo_nombre_subtipo}' agregado", "id": nuevo_id})
    raise HTTPException(status_code=500, detail="Fallo al guardar el subtipo de préstamo")

@router.get("/buscar_equipo/{serie}", response_class=JSONResponse)
async def buscar_equipo(serie: str):
    equipos = cargar_json("equipos.json") # Reemplazado 'inventario.json' por 'equipos.json' si es el archivo que usas para equipos
    equipo = next((e for e in equipos if e.get("serie") == serie), None)
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipo

@router.get("/chips", response_class=JSONResponse)
async def obtener_chips():
    equipos = cargar_json("equipos.json") # Reemplazado 'inventario.json' por 'equipos.json'
    chips = [equipo.get("serie") for equipo in equipos if equipo.get("categoria") == "Comunicación Satelital"]
    return chips

@router.post("/agregar_chip", response_class=JSONResponse)
async def agregar_chip(chip: dict):
    nuevo_serie_chip = chip.get("serie")
    if not nuevo_serie_chip:
        raise HTTPException(status_code=400, detail="Número de serie del chip inválido")

    equipos = cargar_json("equipos.json") # Reemplazado 'inventario.json' por 'equipos.json'
    if any(e.get("serie") == nuevo_serie_chip for e in equipos):
        raise HTTPException(status_code=400, detail="Chip con ese número de serie ya existe")
    
    # Generar un ID único (UUID es más fiable)
    nuevo_id = str(uuid.uuid4())
    
    equipos.append({
        "id": nuevo_id, # Usar UUID para ID
        "serie": nuevo_serie_chip,
        "categoria": "Comunicación Satelital"
    })
    
    if guardar_json("equipos.json", equipos): # Reemplazado 'inventario.json' por 'equipos.json'
        return JSONResponse(status_code=201, content={"mensaje": f"Chip '{nuevo_serie_chip}' agregado"})
    raise HTTPException(status_code=500, detail="Fallo al guardar el chip")

# ===========================
# Ruta para mostrar la página de préstamos (protegida)
# ===========================
@router.get("/", response_class=HTMLResponse)
async def prestamos_page(request: Request, usuario_logueado: dict = Depends(validar_token)):
    # print(f"DEBUG: Acceso a prestamos para usuario: {usuario_logueado.get('usuario')}") # Limpiamos los prints de debug
    return templates.TemplateResponse("prestamos.html", {"request": request})


# ===========================
# NUEVA RUTA: Recibir y guardar datos del préstamo
# ===========================
@router.post("/finalizar-prestamo", response_class=JSONResponse)  # Renombrado para coincidir con el frontend
async def finalizar_prestamo(request: Request, usuario_logueado: dict = Depends(validar_token)):
    try:
        # Los datos vendrán como JSON en el cuerpo de la solicitud
        data = await request.json()
        print(f"DEBUG: Datos recibidos para finalizar préstamo: {data}")  # Imprimir los datos recibidos para depuración

        # Validaciones básicas de los datos recibidos
        responsable_entrega = data.get("entrega", {}).get("responsable")
        tipo_prestamo = data.get("entrega", {}).get("tipo_prestamo")
        equipos_prestados = data.get("equipos", [])

        if not responsable_entrega:
            raise HTTPException(status_code=400, detail="El responsable de entrega es obligatorio.")
        if not tipo_prestamo:
            raise HTTPException(status_code=400, detail="El tipo de préstamo es obligatorio.")
        if not equipos_prestados:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos un equipo para el préstamo.")

        # Generar un ID único para el préstamo
        prestamo_id = str(uuid.uuid4())

        # Crear el objeto de préstamo con un timestamp
        nuevo_prestamo = {
            "id": prestamo_id,
            "fecha_prestamo": datetime.now().isoformat(),  # Guarda la fecha y hora actual en formato ISO 8601
            "responsable_entrega": responsable_entrega,
            "responsable_devolucion": data.get("responsable_devolucion", None),  # Puede ser nulo al inicio
            "tipo_prestamo": tipo_prestamo,
            "detalle_prestamo": data.get("entrega", {}).get("detalle_prestamo"),
            "equipos_prestados": equipos_prestados,  # Lista de equipos
            "estado": "Activo",  # O "Pendiente", "Prestado", etc.
            "usuario_registro": usuario_logueado.get("usuario")  # Quien registró el préstamo
        }

        # Cargar los préstamos existentes usando la función de json_db
        prestamos_existentes = get_prestamos()
        prestamos_existentes.append(nuevo_prestamo)

        # Guardar los préstamos actualizados usando la función de json_db
        if save_prestamos(prestamos_existentes):
            print(f"DEBUG: Préstamo {prestamo_id} guardado exitosamente.")  # Imprimir mensaje de éxito
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"mensaje": "Préstamo registrado exitosamente", "prestamo_id": prestamo_id}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Fallo al guardar el préstamo en el archivo JSON"
            )

    except HTTPException as e:
        # Re-lanza las excepciones HTTPException generadas por dependencias o validaciones
        raise e
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"ERROR: Error al procesar la solicitud de finalizar préstamo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar los datos del préstamo: {e}"
        )