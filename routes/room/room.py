from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from models.room import RoomManager
from dotenv import load_dotenv
import os

load_dotenv()

# Obtén la cadena de conexión desde la variable de entorno
mongo_uri = os.getenv('MONGO_URI')

# Verifica si la cadena de conexión está presente
if not mongo_uri:
    raise ValueError("La variable de entorno MONGO_URI no está configurada.")

# Crea el cliente de MongoDB
mongo_client = MongoClient(mongo_uri)
room_manager = RoomManager(mongo_client, 'hotel', 'rooms')

room_blueprint = Blueprint('room_blueprint', __name__)

@room_blueprint.route('/rooms', methods=['GET'])
def get_rooms():
    rooms = room_manager.get_rooms()
    rooms_info = [room.__dict__ for room in rooms]
    return jsonify(rooms_info), 200


@room_blueprint.route('/find-rooms', methods=['POST'])
def find_rooms():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400
    
    num_people = json_data.get('num_people')
    start_date = json_data.get('start_date')
    end_date = json_data.get('end_date')
    num_rooms = json_data['num_rooms']

    if not all([num_people, start_date, end_date, num_rooms]):
        return jsonify({"message": "Missing required parameters (num_people, start_date, end_date, num_rooms)"}), 400

    room_combinations = room_manager.find_room_combinations(num_people, start_date, end_date, num_rooms)

    # Convertir cada combinación de habitaciones a su representación JSON
    combinations_json = []
    for combo in room_combinations:
        rooms_in_combo = combo['rooms']
        rooms_info = [room.__dict__ for room in rooms_in_combo]  # Convertir cada objeto Room a dict
        combo_info = {
            "rooms": rooms_info,
            "total_capacity": combo['total_capacity'],
            "excess_capacity": combo['excess_capacity']
        }
        combinations_json.append(combo_info)

    return jsonify(combinations_json), 200
