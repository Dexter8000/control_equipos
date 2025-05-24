from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "Salayer*109"  # Reemplaza con la contraseña original
hashed_password = pwd_context.hash(password)

print("Nuevo hash:", hashed_password)

