import pyodbc

def conectar_db():
    conexion = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=127.0.0.1,1433;"  # Aquí usamos el puerto correcto
        "DATABASE=bd_control_equipos;"
        "UID=sa;"
        "PWD=Salayer*109;"
    )
    return conexion
