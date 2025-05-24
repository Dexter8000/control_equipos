from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from routers.auth import validar_token
from json_db import cargar_json, guardar_json

router = APIRouter()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ver usuarios (Ruta: /usuarios)
@router.get("/", response_class=HTMLResponse)
async def ver_usuarios(
    request: Request,
    usuario_logueado: dict = Depends(validar_token),
    mensaje: str = ""
):
    usuarios = cargar_json("usuarios.json")
    print("Usuarios cargados:", usuarios)  # Depuración: Imprimir la lista de usuarios cargados
    return templates.TemplateResponse("usuarios.html", {
        "request": request,
        "usuarios": usuarios,
        "usuario": usuario_logueado["usuario"],
        "mensaje": mensaje
    })


# Agregar nuevo usuario (Ruta: /usuarios/agregar)
@router.post("/agregar")
async def agregar_usuario(
    request: Request,
    usuario: str = Form(...),
    contrasena: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    rol: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    usuarios = cargar_json("usuarios.json")
    if any(u["usuario"] == usuario for u in usuarios):
        return RedirectResponse("/usuarios?mensaje=⚠️ El usuario ya existe", status_code=303)

    nuevo_id = f"USR{len(usuarios)+1:03d}"
    hash_contra = pwd_context.hash(contrasena)

    nuevo_usuario = {
        "id": nuevo_id,
        "usuario": usuario,
        "contrasena": hash_contra,
        "nombre": nombre,
        "apellido": apellido,
        "rol": rol
    }

    usuarios.append(nuevo_usuario)
    guardar_json("data/usuarios.json", usuarios)

    return RedirectResponse("/usuarios?mensaje=✅ Usuario agregado correctamente", status_code=303)

# Eliminar usuario (Ruta: /usuarios/eliminar)
@router.post("/eliminar")
async def eliminar_usuario(
    usuario: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    usuarios = cargar_json("usuarios.json")
    usuarios = [u for u in usuarios if u["usuario"] != usuario]
    guardar_json("data/usuarios.json", usuarios)
    return RedirectResponse("/usuarios", status_code=303)
