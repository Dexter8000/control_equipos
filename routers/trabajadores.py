from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from routers.auth import validar_token
from json_db import cargar_json, guardar_json
from typing import List, Optional
from fuzzywuzzy import fuzz

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Jerarquía de rangos
JERARQUIA_RANGOS = [
    "SUBCOMISIONADO",
    "MAYOR",
    "CAPITAN",
    "TENIENTE",
    "SUBTENIENTE",
    "SARGENTO 1RO.",
    "SARGENTO 2DO.",
    "CABO 1RO.",
    "CABO 2DO.",
    "GUARDIA",
]
RANGO_A_ORDEN = {rango: i for i, rango in enumerate(JERARQUIA_RANGOS)}

def ordenar_por_jerarquia(trabajadores: List[dict]):
    return sorted(trabajadores, key=lambda t: RANGO_A_ORDEN.get(t["rango"], len(JERARQUIA_RANGOS)))

def fuzzy_match(texto_busqueda: str, texto_original: str, threshold: int = 80) -> bool:
    if not texto_busqueda or not texto_original:
        return False
    return fuzz.partial_ratio(texto_busqueda.lower(), texto_original.lower()) >= threshold

@router.get("/", response_class=HTMLResponse)
async def ver_trabajadores(
    request: Request,
    usuario_logueado: dict = Depends(validar_token),
    departamento: Optional[str] = None,
    global_search: Optional[str] = None,
    mensaje: str = ""
):
    empleados = cargar_json("data/Trabajadores.json")
    departamentos_data = cargar_json("data/departamentos.json")
    departamentos_dict = {d["id"]: d["nombre"] for d in departamentos_data}

    empleados_con_nombre_departamento = []
    for empleado in empleados:
        departamento_id = empleado.get("departamento_id")
        departamento_nombre = departamentos_dict.get(departamento_id, "Departamento Desconocido")
        empleado_con_nombre = empleado.copy()
        empleado_con_nombre["nombre_departamento"] = departamento_nombre
        empleados_con_nombre_departamento.append(empleado_con_nombre)

    resultados_departamento_ordenado = []
    resumen_rangos = {}
    resultados_global = []
    trabajadores_a_contar = []

    if departamento:
        resultados_departamento = [
            e for e in empleados_con_nombre_departamento if fuzzy_match(departamento, e["nombre_departamento"])
        ]
        resultados_departamento_ordenado = ordenar_por_jerarquia(resultados_departamento)
        trabajadores_a_contar = resultados_departamento
    elif global_search:
        for empleado in empleados_con_nombre_departamento:
            if (fuzzy_match(global_search, empleado.get("placa", "")) or
                fuzzy_match(global_search, empleado.get("rango", "")) or
                fuzzy_match(global_search, empleado.get("nombre", "")) or
                fuzzy_match(global_search, empleado.get("apellido", ""))):
                resultados_global.append(empleado)
        trabajadores_a_contar = resultados_global

    if trabajadores_a_contar:
        resumen_rangos = {}
        for rango in JERARQUIA_RANGOS:
            count = sum(1 for e in trabajadores_a_contar if e["rango"].lower() == rango.lower())
            if count > 0:
                resumen_rangos[rango] = count

    return templates.TemplateResponse("Trabajadores.html", {
        "request": request,
    "empleados": empleados_con_nombre_departamento,
    "departamentos": [{"id": d, "nombre": n} for d, n in departamentos_dict.items()],
    "usuario": usuario_logueado["usuario"],  # SOLO PASAR usuario
    "resultados_departamento_ordenado": resultados_departamento_ordenado,
    "resumen_rangos": resumen_rangos,
    "resultados_global": resultados_global,
    "busqueda_departamento": departamento,
    "busqueda_global": global_search,
    "mensaje": mensaje
    })

@router.post("/buscar_departamento", response_class=HTMLResponse)
async def buscar_departamento(request: Request, departamento: str = Form(...), usuario_logueado: dict = Depends(validar_token)):
    return await ver_trabajadores(request, usuario_logueado=usuario_logueado, departamento=departamento)

@router.post("/buscar_global", response_class=HTMLResponse)
async def buscar_global(request: Request, global_search: str = Form(...), usuario_logueado: dict = Depends(validar_token)):
    return await ver_trabajadores(request, usuario_logueado=usuario_logueado, global_search=global_search)

@router.post("/editar")
async def editar_trabajador(
    placa: str = Form(...),
    rango: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    departamento_id: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("data/Trabajadores.json")
    for emp in empleados:
        if emp["placa"] == placa:
            emp["rango"] = rango
            emp["nombre"] = nombre
            emp["apellido"] = apellido
            emp["departamento_id"] = departamento_id
            break
    guardar_json("data/Trabajadores.json", empleados)
    return RedirectResponse(url="/trabajadores?mensaje=✅ Datos actualizados", status_code=303)

@router.post("/agregar")
async def agregar_trabajador(
    placa: str = Form(...),
    rango: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    departamento_id: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("data/Trabajadores.json")
    if any(e["placa"] == placa for e in empleados):
        return RedirectResponse(url="/trabajadores?mensaje=⚠️ Placa ya existe", status_code=303)

    nuevo_empleado = {
        "id": f"EMP{len(empleados)+1:03d}",
        "placa": placa,
        "rango": rango,
        "nombre": nombre,
        "apellido": apellido,
        "departamento_id": departamento_id,
        "historial_prestamos": []
    }
    empleados.append(nuevo_empleado)
    guardar_json("data/Trabajadores.json", empleados)
    return RedirectResponse(url="/trabajadores?mensaje=✅ Trabajador agregado", status_code=303)

@router.post("/eliminar")
async def eliminar_trabajador(
    placa: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("data/Trabajadores.json")
    empleados = [e for e in empleados if e["placa"] != placa]
    guardar_json("data/Trabajadores.json", empleados)
    return RedirectResponse(url="/trabajadores?mensaje=✅ Trabajador eliminado", status_code=303)

@router.get("/contador")
async def obtener_total_trabajadores(usuario_logueado: dict = Depends(validar_token)):
    empleados = cargar_json("data/Trabajadores.json")
    return {"total": len(empleados)}
