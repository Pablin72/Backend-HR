from pymongo import MongoClient
from entities.user import User
from dotenv import load_dotenv
load_dotenv
import os
mongo_uri = os.getenv('MONGO_URI')


# Conectar a la base de datos MongoDB
mongo_client = MongoClient(mongo_uri)

# Crear una instancia del User
user = User(
    _id=1,
    gov_id=1721533253,
    name="Pablo",
    lastname="Arcos",
    email="pablodarcos.723@gmail.com",
    phone_number="0995570828",
    birth="2003-02-07"
)

# Mostrar información del usuario
print("Información del usuario:")
print("User ID:", user._id)
print("Nombre completo:", user.name, user.lastname)
print("Email:", user.email)
print("Teléfono:", user.phone_number)
print("Fecha de nacimiento:", user.birth)
print()

# Guardar el usuario en MongoDB (puedes ajustar la conexión y la colección)
db = mongo_client['hotel']
collection = db['users']
collection.insert_one(user.__dict__)

# Consultar el usuario desde MongoDB por su ID
user_id_to_query = 1
user_data_from_db = collection.find_one({'_id': user_id_to_query})

# Mostrar la información del usuario desde la base de datos
if user_data_from_db:
    user_from_db = User.from_dict(user_data_from_db)
    print("Información del usuario desde la base de datos:")
    print("User ID:", user_from_db._id)
    print("Nombre completo:", user_from_db.name, user_from_db.lastname)
    print("Email:", user_from_db.email)
    print("Teléfono:", user_from_db.phone_number)
    print("Fecha de nacimiento:", user_from_db.birth)
else:
    print(f"No se encontró un usuario con ID {user_id_to_query} en la base de datos.")
