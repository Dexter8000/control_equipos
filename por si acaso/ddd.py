from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from json_db import get_usuarios # Asegúrate de que json_db esté accesible y get_usuarios funcione.

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# =======================
# Configuración de Seguridad
# =======================
SECRET_KEY = "ClaveMuySecretaQueDebesCambiar"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =======================
# Hasheo de contraseñas
# =======================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/")

# =======================
# Ruta GET login
# =======================
@router.get("/", response_class=HTMLResponse)
async def mostrar_login(request: Request):
    print("DEBUG: Mostrando formulario de login")  # Depuración
    return templates.TemplateResponse("login.html", {"request": request, "mensaje": ""})

# =======================
# Ruta POST para login
# =======================
@router.post("/", response_class=HTMLResponse)
async def procesar_login(request: Request, usuario: str = Form(...), password: str = Form(...)):
    print(f"DEBUG: Intentando autenticar al usuario: {usuario}")  # Depuración
    usuarios = get_usuarios()
    for u in usuarios:
        if u["usuario"] == usuario and pwd_context.verify(password, u["contrasena"]):
            # Autenticación exitosa → crear token
            token_data = {
                "sub": u["usuario"],
                "nombre": u["nombre"],
                "apellido": u["apellido"],
                "rol": u["rol"],
                "id": u["id"]
            }
            expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = jwt.encode({**token_data, "exp": datetime.utcnow() + expire}, SECRET_KEY, algorithm=ALGORITHM)

            response = RedirectResponse(url="/dashboard", status_code=302)
            response.set_cookie(key="token", value=token, httponly=True)
            print(f"DEBUG: Cookie 'token' establecida para usuario {usuario}. Valor: {token[:20]}... (primeros 20 caracteres)") # <-- **Línea de depuración clave**
            print(f"DEBUG: Redirigiendo a /dashboard con token establecido.") # Depuración
            return response

    # Si falla autenticación
    print(f"DEBUG: Autenticación fallida para el usuario: {usuario}")  # Depuración
    return templates.TemplateResponse("login.html", {
        "request": request,
        "mensaje": "⚠️ Usuario o contraseña incorrecta."
    })

# =======================
# Validar token
# =======================
def validar_token(token: str = Depends(oauth2_scheme)):
    print(f"DEBUG: validar_token llamado. Token recibido: {token[:20]}... (primeros 20 caracteres)") # <-- **Línea de depuración clave**
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"DEBUG: Token decodificado exitosamente. Payload: {payload}") # Depuración
        usuario = payload.get("sub")
        if not usuario:
            print("ERROR: Token inválido, usuario no encontrado en payload.") # Depuración
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        print(f"DEBUG: Token válido para usuario: {usuario}. Rol: {payload.get('rol')}") # Depuración
        return {
            "id": payload.get("id"),
            "usuario": usuario,
            "nombre": payload.get("nombre"),
            "apellido": payload.get("apellido"),
            "rol": payload.get("rol")
        }
    except JWTError as e:
        print(f"ERROR: Fallo al validar token: {e}")  # <-- **Línea de depuración clave**
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")