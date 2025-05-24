from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from routers.auth import validar_token
from json_db import cargar_json, guardar_json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/devoluciones", response_class=HTMLResponse)
async def ver_devoluciones(request: Request, usuario_logueado: dict = Depends(validar_token)):
    devoluciones = cargar_json("data/devoluciones.json")
    prestamos = cargar_json("data/prestamos.json")
    inventario = cargar_json("data/inventario.json")
    trabajadores = cargar_json("data/Trabajadores.json")
    return templates.TemplateResponse("Devoluciones.html", {
        "request": request,
        "devoluciones": devoluciones,
        "prestamos": prestamos,
        "inventario": inventario,
        "trabajadores": trabajadores,
        "usuario": usuario_logueado["usuario"],
        "nombre": usuario_logueado["nombre"],
        "apellido": usuario_logueado["apellido"]
    })

@router.post("/devoluciones/marcar_pendiente")
async def marcar_devolucion_pendiente(prestamo_id: str = Form(...), usuario_logueado: dict = Depends(validar_token)):
    prestamos = cargar_json("data/prestamos.json")
    devoluciones = cargar_json("data/devoluciones.json")

    prestamo = next((p for p in prestamos if p["id"] == prestamo_id), None)

    if not prestamo or prestamo["estado"] != "Activo":
        return RedirectResponse("/devoluciones?mensaje=⚠️ El préstamo no existe o ya fue devuelto", status_code=303)

    nueva_devolucion = {
        "id": f"DEV{len(devoluciones)+1:03d}",
        "prestamo_id": prestamo_id,
        "equipo_id": prestamo["equipo_id"],
        "trabajador_placa": prestamo["trabajador_placa"],
        "fecha_esperada": prestamo["fecha_devolucion_esperada"],
        "fecha_real": None,
        "estado": "Pendiente",
        "usuario_responsable": usuario_logueado["usuario"]
    }
    devoluciones.append(nueva_devolucion)
    guardar_json("data/devoluciones.json", devoluciones)

    return RedirectResponse("/devoluciones?mensaje=✅ Devolución marcada como pendiente", status_code=303)

@router.post("/devoluciones/registrar_devolucion")
async def registrar_devolucion(
    devolucion_id: str = Form(...),
    fecha_real_devolucion: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    devoluciones = cargar_json("data/devoluciones.json")
    prestamos = cargar_json("data/prestamos.json")
    inventario = cargar_json("data/inventario.json")

    devolucion = next((d for d in devoluciones if d["id"] == devolucion_id), None)

    if not devolucion or devolucion["estado"] != "Pendiente":
        return RedirectResponse("/devoluciones?mensaje=⚠️ La devolución no existe o ya fue registrada", status_code=303)

    devolucion["fecha_real"] = fecha_real_devolucion
    devolucion["estado"] = "Completada"
    guardar_json("data/devoluciones.json", devoluciones)

    prestamo_id = devolucion["prestamo_id"]
    prestamo = next((p for p in prestamos if p["id"] == prestamo_id), None)
    if prestamo:
        prestamo["fecha_devolucion_real"] = fecha_real_devolucion
        prestamo["estado"] = "Devuelto"
        guardar_json("data/prestamos.json", prestamos)

        equipo_id = prestamo["equipo_id"]
        for item in inventario:
            if item["id"] == equipo_id:
                item["estado"] = "Disponible"
                break
            elif "perifericos" in item:
                for perif in item["perifericos"]:
                    if perif["id"] == equipo_id:
                        perif["estado"] = "Disponible"
                        break
        guardar_json("data/inventario.json", inventario)

    return RedirectResponse("/devoluciones?mensaje=✅ Devolución registrada", status_code=303)
