# verificar_hash.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

contrasena_plana = "Salayer*109"
hash_generado = pwd_context.hash(contrasena_plana)
print(f"Hash generado para '{contrasena_plana}': {hash_generado}")

# Este es el hash para 'admin2' que tienes en tu usuarios.json
hash_de_admin2_en_json = "$2b$12$aKGaBFxJ0xCiP0t4rxrPJuQAYaMCltx/x2VQskfctxuNtBTUZmg3e" # Copiado de tu usuarios.json

es_correcta = pwd_context.verify(contrasena_plana, hash_de_admin2_en_json)
print(f"¿La contraseña plana '{contrasena_plana}' coincide con el hash del JSON? {es_correcta}")