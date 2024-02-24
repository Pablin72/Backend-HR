from flask import Flask
from pymongo import MongoClient
import entities.room as room

app = Flask(__name__)

from dotenv import load_dotenv
load_dotenv
import os
mongo_uri = os.getenv('MONGO_URI')


# Conectar a la base de datos MongoDB
mongo_client = MongoClient(mongo_uri)
mongo = MongoClient(app.config['MONGO_URI'])

# Comprobación de la conexión
try:
    # Intenta acceder a la base de datos para comprobar la conexión
    mongo.server_info()
    print("Conexio n exitosa a la base de datos 'hotel'")
except Exception as e:
    print("Error de conexión:", e)


if __name__ == "__main__":
    # Configuración de la conexión a la base de datos usando la instancia de Flask y pymongo
    db_name = 'hotel'
    collection_name = 'rooms'

    # Crear una instancia de HabitacionManager con el cliente de MongoDB ya establecido
    habitacion_manager = room.RoomManager(mongo, db_name, collection_name)

    # Obtener habitaciones desde la base de datos
    habitaciones = habitacion_manager.get_rooms()

    # Imprimir información de las habitaciones
    for habitacion in habitaciones:
        print(f"ID: {habitacion._id}, Tipo: {habitacion.room_type},  Descripción: {habitacion.description},Precio: {habitacion.price}, Disponible: {not habitacion.occupancy}")
