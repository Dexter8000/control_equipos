from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from json_db import cargar_json, guardar_json
import os

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
    usuarios = cargar_json("data/usuarios.json")
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

def validar_token(request: Request):
    token = request.cookies.get("token")
    if token is None:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario = payload.get("sub")
        nombre = payload.get("nombre")
        apellido = payload.get("apellido")
        rol = payload.get("rol")
        id_usuario = payload.get("id")
        if usuario is None:
            raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/"})
        return {"id": id_usuario, "usuario": usuario, "nombre": nombre, "apellido": apellido, "rol": rol}
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
            "apellido": usuario["apellido"],
            "rol": usuario["rol"],
            "id": usuario["id"]
        }, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    mensaje = "Usuario o contraseña incorrectos"
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": mensaje})

# ---------------- DASHBOARD ----------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, usuario_logueado: dict = Depends(validar_token)):
    usuarios = cargar_json("data/usuarios.json")
    inventario = cargar_json("data/inventario.json")
    equipos_disponibles = sum(1 for equipo in inventario if equipo.get("estado") == "Disponible")

    prestamos = cargar_json("data/prestamos.json")
    prestamos_activos = len(prestamos)

    devoluciones = cargar_json("data/devoluciones.json")
    devoluciones_pendientes = sum(1 for devolucion in devoluciones if devolucion.get("estado") == "Pendiente")

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

@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("token")
    return response

# ---------------- VISTA DE USUARIOS ----------------
@app.get("/usuarios", response_class=HTMLResponse)
async def ver_usuarios(request: Request, usuario_logueado: dict = Depends(validar_token), mensaje: str = ""):
    usuarios = cargar_json("data/usuarios.json")
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
    usuarios = cargar_json("data/usuarios.json")

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

# ---------------- ELIMINAR USUARIO ----------------
@app.post("/usuarios/eliminar")
async def eliminar_usuario(
    usuario: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    usuarios = cargar_json("data/usuarios.json")
    usuarios = [u for u in usuarios if u["usuario"] != usuario]
    guardar_json("data/usuarios.json", usuarios)
    return RedirectResponse("/usuarios", status_code=303)

# ---------------- VISTA DE TRABAJADORES ----------------
@app.get("/trabajadores", response_class=HTMLResponse)
async def ver_trabajadores(request: Request, usuario_logueado: dict = Depends(validar_token)):
    empleados = cargar_json("data/Trabajadores.json")
    departamentos_data = cargar_json("data/departamentos.json")
    departamentos = [{"id": d["id"], "nombre": d["nombre"]} for d in departamentos_data]

    return templates.TemplateResponse("Trabajadores.html", {
        "request": request,
        "empleados": empleados,
        "departamentos": departamentos,
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
    empleados = cargar_json("data/Trabajadores.json")
    for emp in empleados:
        if emp["placa"] == placa:
            emp["rango"] = rango
            emp["nombre"] = nombre
            emp["apellido"] = apellido
            emp["departamento_id"] = departamento_id
            break
    guardar_json("data/Trabajadores.json", empleados)
    return RedirectResponse("/trabajadores", status_code=303)

# ---------------- AGREGAR TRABAJADOR ----------------
@app.post("/trabajadores/agregar")
async def agregar_trabajador(
    request: Request,
    placa: str = Form(...),
    rango: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    departamento_id: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("data/Trabajadores.json")
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
    guardar_json("data/Trabajadores.json", empleados)
    return RedirectResponse("/trabajadores?mensaje=✅ Trabajador agregado", status_code=303)

@app.post("/trabajadores/eliminar")
async def eliminar_trabajador(
    placa: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    empleados = cargar_json("data/Trabajadores.json")
    empleados = [e for e in empleados if e["placa"] != placa]
    guardar_json("data/Trabajadores.json", empleados)
    return RedirectResponse("/trabajadores", status_code=303)

@app.get("/trabajadores/contador")
async def obtener_total_trabajadores(usuario_logueado: dict = Depends(validar_token)):
    empleados = cargar_json("data/Trabajadores.json")
    return {"total": len(empleados)}

# ---------------- VISTA DE EQUIPOS ----------------
@app.get("/equipos", response_class=HTMLResponse)
async def ver_equipos(request: Request, usuario_logueado: dict = Depends(validar_token)):
    inventario = cargar_json("data/inventario.json")
    categorias_data = cargar_json("data/categorias.json")
    subcategorias_data = cargar_json("data/subcategorias.json")
    departamentos_data = cargar_json("data/departamentos.json")

    categorias = [{"id": c["id"], "nombre": c["nombre"]} for c in categorias_data]
    subcategorias = [{"id": s["id"], "nombre": s["nombre"]} for s in subcategorias_data]
    departamentos = [{"id": d["id"], "nombre": d["nombre"]} for d in departamentos_data]

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

@app.post("/equipos/actualizar")
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
                    inventario[idx]["perifericos"][p_idx] = data
                    actualizado = True
                    break

    if actualizado:
        guardar_json("data/inventario.json", inventario)
        return JSONResponse(content={"mensaje": "Equipo actualizado correctamente"})
    else:
        return JSONResponse(content={"mensaje": "No se encontró el equipo para actualizar"}, status_code=404)

@app.post("/equipos/agregar")
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
            "periferico": form_data.get("periferico"),
        }

        inventario.append(nuevo_equipo)
        guardar_json("data/inventario.json", inventario)
        return JSONResponse(content={"success": True})

    except Exception as e:
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=400
        )

@app.post("/equipos/agregar_periferico")
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
            "periferico": equipo_principal_id,
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
        return JSONResponse(
            content={"success": False, "error": str(e)},
            status_code=400
        )

# ---------------- VISTA DE PRÉSTAMOS ----------------
@app.get("/prestamos", response_class=HTMLResponse)
async def ver_prestamos(request: Request, usuario_logueado: dict = Depends(validar_token)):
    prestamos = cargar_json("data/prestamos.json")
    inventario = cargar_json("data/inventario.json")
    trabajadores = cargar_json("data/Trabajadores.json")
    return templates.TemplateResponse("Prestamos.html", {
        "request": request,
        "prestamos": prestamos,
        "inventario": inventario,
        "trabajadores": trabajadores,
        "usuario": usuario_logueado["usuario"],
        "nombre": usuario_logueado["nombre"],
        "apellido": usuario_logueado["apellido"]
    })

@app.post("/prestamos/realizar")
async def realizar_prestamo(
    request: Request,
    equipo_id: str = Form(...),
    trabajador_placa: str = Form(...),
    fecha_prestamo: str = Form(...),
    fecha_devolucion_esperada: str = Form(...),
    notas: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    prestamos = cargar_json("data/prestamos.json")
    inventario = cargar_json("data/inventario.json")
    trabajadores = cargar_json("data/Trabajadores.json")

    equipo = next((e for e in inventario if e["id"] == equipo_id), None)
    trabajador = next((t for t in trabajadores if t["placa"] == trabajador_placa), None)

    if not equipo or equipo.get("estado") != "Disponible":
        return RedirectResponse("/prestamos?mensaje=⚠️ El equipo no está disponible o no existe", status_code=303)
    if not trabajador:
        return RedirectResponse("/prestamos?mensaje=⚠️ El trabajador no existe", status_code=303)

    nuevo_prestamo = {
        "id": f"PRE{len(prestamos)+1:03d}",
        "equipo_id": equipo_id,
        "trabajador_placa": trabajador_placa,
        "fecha_prestamo": fecha_prestamo,
        "fecha_devolucion_esperada": fecha_devolucion_esperada,
        "fecha_devolucion_real": None,
        "estado": "Activo",
        "notas": notas,
        "usuario_responsable": usuario_logueado["usuario"]
    }
    prestamos.append(nuevo_prestamo)
    guardar_json("data/prestamos.json", prestamos)

    # Actualizar el estado del equipo a "Prestado"
    for item in inventario:
        if item["id"] == equipo_id:
            item["estado"] = "Prestado"
            break
        elif "perifericos" in item:
            for perif in item["perifericos"]:
                if perif["id"] == equipo_id:
                    perif["estado"] = "Prestado"
                    break
    guardar_json("data/inventario.json", inventario)
    # Agregar el préstamo al historial del trabajador
    for t in trabajadores:
        if t["placa"] == trabajador_placa:
            t["historial_prestamos"].append(nuevo_prestamo["id"])
            break
    guardar_json("data/Trabajadores.json", trabajadores)

    return RedirectResponse("/prestamos?mensaje=✅ Préstamo realizado correctamente", status_code=303)

@app.post("/prestamos/devolver")
async def realizar_devolucion(
    prestamo_id: str = Form(...),
    fecha_devolucion_real: str = Form(...),
    usuario_logueado: dict = Depends(validar_token)
):
    prestamos = cargar_json("data/prestamos.json")
    inventario = cargar_json("data/inventario.json")

    prestamo = next((p for p in prestamos if p["id"] == prestamo_id), None)

    if not prestamo or prestamo["estado"] != "Activo":
        return RedirectResponse("/prestamos?mensaje=⚠️ El préstamo no existe o ya fue devuelto", status_code=303)

    prestamo["fecha_devolucion_real"] = fecha_devolucion_real
    prestamo["estado"] = "Devuelto"
    guardar_json("data/prestamos.json", prestamos)

    # Actualizar el estado del equipo a "Disponible"
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

    return RedirectResponse("/prestamos?mensaje=✅ Devolución registrada correctamente", status_code=303)

# ---------------- VISTA DE DEVOLUCIONES ----------------
@app.get("/devoluciones", response_class=HTMLResponse)
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

@app.post("/devoluciones/marcar_pendiente")
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

@app.post("/devoluciones/registrar_devolucion")
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

    # Actualizar el estado del préstamo a "Devuelto"
    prestamo_id = devolucion["prestamo_id"]
    prestamo = next((p for p in prestamos if p["id"] == prestamo_id), None)
    if prestamo:
        prestamo["fecha_devolucion_real"] = fecha_real_devolucion
        prestamo["estado"] = "Devuelto"
        guardar_json("data/prestamos.json", prestamos)

        # Actualizar el estado del equipo a "Disponible"
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
