import pyodbc

try:
    conexion = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=127.0.0.1,1433;"
        "DATABASE=bd_control_equipos;"
        "UID=sa;"
        "PWD=Salayer*109;"
    )
    print("✅ Conexión exitosa a SQL Server")
    conexion.close()
except Exception as e:
    print("❌ Error en la conexión:", e)
