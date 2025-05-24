from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generar_hash(password):
    return pwd_context.hash(password)

# Ejemplo
if __name__ == "__main__":
    password_plana = input("Escribe la contraseña a encriptar: ")
    hash_generado = generar_hash(password_plana)
    print("🔐 Contraseña hasheada:\n", hash_generado)
