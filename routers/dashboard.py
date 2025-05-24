from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routers.auth import validar_token
from json_db import cargar_json
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, usuario_logueado: dict = Depends(validar_token)):
    usuarios = cargar_json("data/usuarios.json")
    inventario = cargar_json("data/inventario.json")
    prestamos = cargar_json("data/prestamos.json")
    devoluciones = cargar_json("data/devoluciones.json")

    equipos_disponibles = sum(1 for equipo in inventario if equipo.get("estado") == "Disponible")
    prestamos_activos = len(prestamos)
    devoluciones_pendientes = sum(1 for d in devoluciones if d.get("estado") == "Pendiente")
    num_usuarios = len(usuarios)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuario": usuario_logueado["usuario"],
        "nombre": usuario_logueado["nombre"],
        "apellido": usuario_logueado["apellido"],
        "rol": usuario_logueado["rol"],
        "num_usuarios": num_usuarios,
        "equipos_disponibles": equipos_disponibles,
        "prestamos_activos": prestamos_activos,
        "devoluciones_pendientes": devoluciones_pendientes,
    })
