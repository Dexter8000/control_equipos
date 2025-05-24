from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# ===========================
# Importar routers del sistema
# ===========================
from routers import (
    auth,
    dashboard,
    usuarios,
    trabajadores,
    equipos,
    prestamos,
    devoluciones,
    data_router
)

from routers.auth import validar_token

# ¡IMPORTANTE! Importa 'initialize_json_files' AQUI
from json_db import get_usuarios, initialize_json_files # <--- AÑADE initialize_json_files aquí

# ===========================
# Inicializar aplicación FastAPI
# ===========================
app = FastAPI(
    title="Sistema de Inventario Inteligente",
    description="API para la gestión de préstamos, devoluciones y usuarios",
    version="1.0.0"
)

# ============================================================
# ¡MUY IMPORTANTE! LLAMA A LA FUNCIÓN DE INICIALIZACIÓN DE ARCHIVOS JSON AQUÍ
# Esto se ejecuta al iniciar el servidor y asegura que 'prestamos.json'
# (y otros archivos) se creen si no existen o están vacíos.
# ============================================================
initialize_json_files()


# ===========================
# Código de depuración adicional para la carga de usuarios
# Este bloque se ejecutará al iniciar el servidor FastAPI
# (Déjalo comentado para producción, solo si lo necesitas para depurar usuarios)
# ===========================
# print("\n--- INICIO DEPURACIÓN DE CARGA DE USUARIOS EN MAIN.PY ---")
# try:
#     test_usuarios = get_usuarios()
#     print(f"DEBUG (main.py startup): get_usuarios() cargó {len(test_usuarios)} usuarios.")
#     for u in test_usuarios:
#         print(f"DEBUG (main.py startup): Usuario encontrado: {u.get('usuario')}")
#     if not test_usuarios:
#         print("ERROR (main.py startup): get_usuarios() devolvió una lista vacía. Asegúrate que usuarios.json contiene datos.")
# except Exception as e:
#     print(f"ERROR (main.py startup): Falló la carga de usuarios en main.py: {e}")
# print("--- FIN DEPURACIÓN DE CARGA DE USUARIOS EN MAIN.PY ---\n")


# ===========================
# Configuración de CORS
# ===========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# Configuración de archivos estáticos y plantillas
# ===========================
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data") # Cuidado si sirves JSON directamente, no es lo ideal para seguridad

templates = Jinja2Templates(directory="templates")

# ===========================
# Incluir todos los routers
# ===========================
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(trabajadores.router, prefix="/trabajadores", tags=["Trabajadores"])
app.include_router(equipos.router, prefix="/equipos", tags=["Equipos"])
app.include_router(prestamos.router, prefix="/prestamos", tags=["Préstamos"])
app.include_router(devoluciones.router, prefix="/devoluciones", tags=["Devoluciones"])
app.include_router(data_router.router)


# ===========================
# Endpoints base
# ===========================

@app.get("/ping")
async def ping():
    return {"mensaje": "Inventario Inteligente activo 🚀"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get("token")
    if token:
        return RedirectResponse(url="/dashboard")
    else:
        return RedirectResponse(url="/auth/")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, usuario_logueado: dict = Depends(validar_token)):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/prestamos", response_class=HTMLResponse)
async def prestamos_page(request: Request, usuario_logueado: dict = Depends(validar_token)):
    return templates.TemplateResponse("prestamos.html", {"request": request})