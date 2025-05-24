# routers/auth.py
from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.security import OAuth2PasswordBearer # <-- ELIMINADO
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from json_db import get_usuarios

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# =======================
# Configuración de Seguridad
# =======================
SECRET_KEY = "ClaveMuySecretaQueDebesCambiar" # ¡Asegúrate de que esta sea la misma en todos tus archivos que la usen!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =======================
# Hasheo de contraseñas
# =======================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/") # <-- ELIMINADO

# =======================
# Ruta GET login
# =======================
@router.get("/", response_class=HTMLResponse)
async def mostrar_login(request: Request):
    # print("DEBUG: Mostrando formulario de login") # Comentado o eliminado
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

# =======================
# Ruta POST para login
# =======================
@router.post("/", response_class=HTMLResponse)
async def procesar_login(request: Request, usuario: str = Form(...), password: str = Form(...)):
    # print(f"DEBUG: Intentando autenticar al usuario: {usuario}") # Comentado o eliminado

    usuarios_cargados = get_usuarios()

    # print(f"DEBUG: 'procesar_login' ha cargado {len(usuarios_cargados)} usuarios desde json_db.") # Comentado o eliminado
    # if not usuarios_cargados:
    #     print("ERROR: La lista de usuarios cargada por get_usuarios() está vacía. ¡Verifica usuarios.json!") # Comentado o eliminado

    usuario_encontrado = None
    for u in usuarios_cargados:
        # print(f"DEBUG: Comparando '{usuario}' con usuario en lista: {u.get('usuario')}") # Comentado o eliminado
        if u["usuario"] == usuario:
            usuario_encontrado = u
            break

    if usuario_encontrado:
        if pwd_context.verify(password, usuario_encontrado["contrasena"]):
            token_data = {
                "sub": usuario_encontrado["usuario"],
                "nombre": usuario_encontrado["nombre"],
                "apellido": usuario_encontrado["apellido"],
                "rol": usuario_encontrado["rol"],
                "id": usuario_encontrado["id"]
            }
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

            response = RedirectResponse(url="/dashboard", status_code=302)
            response.set_cookie(key="token", value=token, httponly=True)
            # print(f"DEBUG: Usuario {usuario} autenticado correctamente. Token establecido.") # Comentado o eliminado
            return response
        else:
            # print(f"DEBUG: Contraseña incorrecta para el usuario: {usuario}") # Comentado o eliminado
            return templates.TemplateResponse("login.html", {
                "request": request,
                "mensaje": "⚠️ Usuario o contraseña incorrecta."
            })
    else:
        # print(f"DEBUG: Usuario '{usuario}' no encontrado en la base de datos (después de cargar la lista).") # Comentado o eliminado
        return templates.TemplateResponse("login.html", {
            "request": request,
            "mensaje": "⚠️ Usuario o contraseña incorrecta."
        })

# =======================
# Validar token
# =======================
async def validar_token(request: Request):
    token = request.cookies.get("token")
    # print(f"DEBUG: validar_token llamado. Token recibido: {token[:20]}... (primeros 20 caracteres)" if token else "DEBUG: validar_token llamado. No se encontró token en cookies.") # Comentado o eliminado

    if not token:
        # print("DEBUG: No se encontró token, redirigiendo a /auth/") # Comentado o eliminado
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/auth/"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(f"DEBUG: Token decodificado exitosamente. Payload: {payload}") # Comentado o eliminado
        usuario = payload.get("sub")
        if not usuario:
            # print("ERROR: Token inválido, usuario no encontrado en payload.") # Comentado o eliminado
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        # print(f"DEBUG: Token válido para usuario: {usuario}. Rol: {payload.get('rol')}") # Comentado o eliminado
        return {
            "id": payload.get("id"),
            "usuario": usuario,
            "nombre": payload.get("nombre"),
            "apellido": payload.get("apellido"),
            "rol": payload.get("rol")
        }
    except JWTError as e:
        # print(f"ERROR: Fallo al validar token: {e}") # Comentado o eliminado
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/auth/"})