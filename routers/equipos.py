from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from routers.auth import validar_token
from json_db import cargar_json, guardar_json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def ver_equipos(request: Request, usuario_logueado: dict = Depends(validar_token)):
    inventario = cargar_json("data/inventario.json")
    categorias = cargar_json("data/categorias.json")
    subcategorias = cargar_json("data/subcategorias.json")
    departamentos = cargar_json("data/departamentos.json")

    return templates.TemplateResponse("Equipos.html", {
        "request": request,
        "inventario": inventario,
        "categorias": categorias,
        "subcategorias": subcategorias,
        "departamentos": departamentos,
        "usuario_actual": usuario_logueado,
        "usuario": usuario_logueado["usuario"],
        "nombre": usuario_logueado["nombre"],
        "apellido": usuario_logueado["apellido"]
    })

@router.post("/equipos/actualizar")
async def actualizar_equipo(request: Request, usuario_logueado: dict = Depends(validar_token)):
    data = await request.json()
    inventario = cargar_json("data/inventario.json")

    actualizado = False
    for idx, equipo in enumerate(inventario):
        if equipo["id"] == data["id"]:
            inventario[idx] = data
            actualizado = True
            break
        elif "perifericos" in equipo:
            for p_idx, perif in enumerate(equipo["perifericos"]):
                if perif["id"] == data["id"]:
                    equipo["perifericos"][p_idx] = data
                    actualizado = True
                    break

    if actualizado:
        guardar_json("data/inventario.json", inventario)
        return JSONResponse(content={"mensaje": "Equipo actualizado correctamente"})
    else:
        return JSONResponse(content={"mensaje": "No se encontró el equipo para actualizar"}, status_code=404)
@router.post("/equipos/agregar")
async def agregar_equipo(request: Request, usuario_logueado: dict = Depends(validar_token)):
    try:
        form_data = await request.form()
        inventario = cargar_json("data/inventario.json")

        nuevo_id = form_data.get("id")
        if any(e["id"] == nuevo_id for e in inventario):
            return JSONResponse(content={"success": False, "error": "⚠️ Ya existe un equipo con ese ID"})

        nuevo_equipo = {
            "id": nuevo_id,
            "nombre": form_data.get("nombre"),
            "marca": form_data.get("marca"),
            "modelo": form_data.get("modelo"),
            "serie": form_data.get("serie"),
            "categoria": form_data.get("categoria"),
            "subcategoria": form_data.get("subcategoria"),
            "estado": form_data.get("estado"),
            "condicion": form_data.get("condicion"),
            "tipo_adquisicion": form_data.get("tipo_adquisicion"),
            "id_departamento_asignado": form_data.get("id_departamento_asignado"),
            "ubicacion_especifica": form_data.get("ubicacion_especifica"),
            "responsable_actual": usuario_logueado["nombre"] + " " + usuario_logueado["apellido"],
            "fecha_creacion": form_data.get("fecha_creacion"),
            "fecha_adquisicion": form_data.get("fecha_adquisicion"),
            "Detalles": form_data.get("Detalles"),
            "periferico": form_data.get("periferico")
        }

        inventario.append(nuevo_equipo)
        guardar_json("data/inventario.json", inventario)
        return JSONResponse(content={"success": True})

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=400)

@router.post("/equipos/agregar_periferico")
async def agregar_periferico(request: Request, usuario_logueado: dict = Depends(validar_token)):
    try:
        form_data = await request.form()
        inventario = cargar_json("data/inventario.json")
        equipo_principal_id = form_data.get("periferico")
        nuevo_periferico = {
            "id": form_data.get("id"),
            "nombre": form_data.get("nombre"),
            "marca": form_data.get("marca"),
            "modelo": form_data.get("modelo"),
            "serie": form_data.get("serie"),
            "categoria": form_data.get("categoria"),
            "subcategoria": form_data.get("subcategoria"),
            "estado": form_data.get("estado"),
            "condicion": form_data.get("condicion"),
            "tipo_adquisicion": form_data.get("tipo_adquisicion"),
            "id_departamento_asignado": form_data.get("id_departamento_asignado"),
            "ubicacion_especifica": form_data.get("ubicacion_especifica"),
            "responsable_actual": usuario_logueado["nombre"] + " " + usuario_logueado["apellido"],
            "fecha_creacion": form_data.get("fecha_creacion"),
            "fecha_adquisicion": form_data.get("fecha_adquisicion"),
            "Detalles": form_data.get("Detalles"),
            "periferico": equipo_principal_id
        }

        encontrado = False
        for equipo in inventario:
            if equipo["id"] == equipo_principal_id:
                if "perifericos" not in equipo:
                    equipo["perifericos"] = []
                equipo["perifericos"].append(nuevo_periferico)
                encontrado = True
                break

        if encontrado:
            guardar_json("data/inventario.json", inventario)
            return JSONResponse(content={"success": True})
        else:
            return JSONResponse(content={"success": False, "error": f"No se encontró el equipo principal con ID: {equipo_principal_id}"}, status_code=404)

    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=400)
