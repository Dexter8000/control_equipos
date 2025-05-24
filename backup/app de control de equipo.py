from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie 
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from json_db import cargar_json, guardar_json

# Seguridad
SECRET_KEY = "ClaveMuySecretaQueDebesCambiar"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Hasheo de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# App y rutas estáticas
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------- AUTENTICACIÓN ----------------
def autenticar_usuario_db(usuario: str, password: str):
    usuarios = cargar_json("usuarios.json")
    for usuario_db in usuarios:
        if usuario_db["usuario"] == usuario:
            if pwd_context.verify(password, usuario_db["contrasena"]):
                return usuario_db
    return None

def crear_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def validar_token(token: str = Cookie(None)):
    if token is None:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario = payload.get("sub")
        nombre = payload.get("nombre")
        apellido = payload.get("apellido")
        if usuario is None:
            raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/"})
        return {"usuario": usuario, "nombre": nombre, "apellido": apellido}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/"})

# ---------------- RUTAS DE LOGIN ----------------
@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

@app.post("/", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    usuario = autenticar_usuario_db(username, password)
    if usuario:
        token = crear_token({
            "sub": usuario["usuario"],
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"]
        }, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    mensaje = "Usuario o contraseña incorrectos"
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": mensaje})

# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, usuario_logueado: dict = Depends(validar_token)):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuario": usuario_logueado["usuario"],
        "nombre": usuario_logueado["nombre"],
        "apellido": usuario_logueado["apellido"]
    })

@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("token")
    return response

# ---------------- VISTA DE USUARIOS ----------------
@app.get("/usuarios", response_class=HTMLResponse)
async def ver_usuarios(request: Request, usuario_logueado: dict = Depends(validar_token), mensaje: str = ""):
    usuarios = cargar_json("usuarios.json")
    return templates.TemplateResponse("usuarios.html", {
        "request": request,
        "usuarios": usuarios,
        "usuario": usuario_logueado["usuario"],
        "mensaje": mensaje
    })

# ---------------- AGREGAR USUARIO ----------------
@app.post("/usuarios/agregar")
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
    guardar_json("usuarios.json", usuarios)

    return RedirectResponse("/usuarios?mensaje=✅ Usuario agregado correctamente", status_code=303)

# ---------------- ELIMINAR USUARIO ----------------
@app.post("/usuarios/eliminar")
async def eliminar_usuario(
    usuario: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    usuarios = cargar_json("usuarios.json")
    usuarios = [u for u in usuarios if u["usuario"] != usuario]
    guardar_json("usuarios.json", usuarios)
    return RedirectResponse("/usuarios", status_code=303)

# ---------------- VISTA DE TRABAJADORES ----------------
@app.get("/trabajadores", response_class=HTMLResponse)
async def ver_trabajadores(request: Request, usuario_logueado: dict = Depends(validar_token)):
    empleados = cargar_json("Trabajadores.json")
    departamentos = cargar_json("departamentos.json")

    mapa_departamentos = {d["id"]: d["nombre"] for d in departamentos}

    # Añadir nombre del departamento al empleado
    for e in empleados:
        e["departamento_nombre"] = mapa_departamentos.get(e["departamento_id"], "Desconocido")

    return templates.TemplateResponse("Trabajadores.html", {
        "request": request,
        "empleados": empleados,
        "usuario": usuario_logueado["usuario"],
        "nombre": usuario_logueado["nombre"],
        "apellido": usuario_logueado["apellido"]
    })


# ---------------- EDITAR TRABAJADOR ----------------
@app.post("/trabajadores/editar")
async def editar_trabajador(
    placa: str = Form(...),
    rango: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    departamento_id: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("Trabajadores.json")
    for emp in empleados:
        if emp["placa"] == placa:
            emp["rango"] = rango
            emp["nombre"] = nombre
            emp["apellido"] = apellido
            emp["departamento_id"] = departamento_id
            break
    guardar_json("Trabajadores.json", empleados)
    return RedirectResponse("/trabajadores", status_code=303)

# ---------------- AGREGAR TRABAJADOR ----------------
@app.post("/trabajadores/agregar")
async def agregar_trabajador(
    placa: str = Form(...),
    rango: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    departamento_id: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("Trabajadores.json")
    if any(e["placa"] == placa for e in empleados):
        return RedirectResponse("/trabajadores?mensaje=⚠️ Placa ya existe", status_code=303)

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
    guardar_json("Trabajadores.json", empleados)
    return RedirectResponse("/trabajadores?mensaje=✅ Trabajador agregado", status_code=303)

@app.post("/trabajadores/eliminar")
async def eliminar_trabajador(
    placa: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("Trabajadores.json")
    empleados = [e for e in empleados if e["placa"] != placa]
    guardar_json("Trabajadores.json", empleados)
    return RedirectResponse("/trabajadores", status_code=303)

@app.get("/trabajadores/contador")
async def obtener_total_trabajadores(usuario_logueado: dict = Depends(validar_token)):
    empleados = cargar_json("Trabajadores.json")
    return {"total": len(empleados)}

# ✅ RUTA FastAPI para mostrar la tabla de equipos
templates = Jinja2Templates(directory="templates")

@app.get("/equipos", response_class=HTMLResponse)
async def ver_equipos(request: Request, usuario_logueado: dict = Depends(validar_token)):
    inventario = cargar_json("inventario.json")
    return templates.TemplateResponse("Equipos.html", {
        "request": request,
        "inventario": inventario,  # ✅ Se pasa al template
        "usuario": usuario_logueado["usuario"],
        "nombre": usuario_logueado["nombre"],
        "apellido": usuario_logueado["apellido"]
        })
@app.post("/equipos/actualizar")
async def actualizar_equipo(request: Request, usuario_logueado: dict = Depends(validar_token)):
    data = await request.json()
    inventario = cargar_json("inventario.json")

    actualizado = False

    # Recorre los equipos principales
    for idx, equipo in enumerate(inventario):
        if equipo["id"] == data["id"]:
            inventario[idx] = data
            actualizado = True
            break
        # Si no es principal, verifica si es un periférico
        elif "perifericos" in equipo:
            for p_idx, perif in enumerate(equipo["perifericos"]):
                if perif["id"] == data["id"]:
                    inventario[idx]["perifericos"][p_idx] = data
                    actualizado = True
                    break

    if actualizado:
        guardar_json("inventario.json", inventario)
        return {"mensaje": "Equipo actualizado correctamente"}
    else:
        return {"mensaje": "No se encontró el equipo para actualizar"}
    @app.post("/equipos/agregar")
async def agregar_equipo(
    id: str = Form(...),
    nombre: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    serie: str = Form(...),
    categoria: str = Form(...),
    subcategoria: str = Form(...),
    estado: str = Form(...),
    condicion: str = Form(...),
    tipo_adquisicion: str = Form(...),
    id_departamento_asignado: str = Form(...),
    ubicacion_especifica: str = Form(...),
    responsable_actual: str = Form(...),
    fecha_creacion: str = Form(...),
    fecha_adquisicion: str = Form(...),
    Detalles: str = Form(...),
    periferico: str = Form(...)
):
    inventario = cargar_json("inventario.json")

    nuevo_equipo = {
        "id": id,
        "nombre": nombre,
        "marca": marca,
        "modelo": modelo,
        "serie": serie,
        "categoria": categoria,
        "subcategoria": subcategoria,
        "estado": estado,
        "condicion": condicion,
        "tipo_adquisicion": tipo_adquisicion,
        "id_departamento_asignado": id_departamento_asignado,
        "ubicacion_especifica": ubicacion_especifica,
        "responsable_actual": responsable_actual,
        "fecha_creacion": fecha_creacion,
        "fecha_adquisicion": fecha_adquisicion,
        "Detalles": Detalles,
        "periferico": periferico
    }

    inventario.append(nuevo_equipo)
    guardar_json("inventario.json", inventario)
    return RedirectResponse("/equipos", status_code=303)