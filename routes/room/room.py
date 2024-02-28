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

@room_blueprint.route('/rooms/<room_id>', methods=['PUT'])
def update_room_occupancy(room_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400
    
    checkin_date = json_data.get('checkin_date')
    checkout_date = json_data.get('checkout_date')

    if not all([checkin_date, checkout_date]):
        return jsonify({"message": "Missing required parameters (checkin_date, checkout_date)"}), 400

    # Obtener la habitación por su ID
    room = room_manager.get_room_by_id(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404

    # Agregar las fechas de check-in y check-out a la lista de ocupación de la habitación
    occupancy_period = {"checkin_date": checkin_date, "checkout_date": checkout_date}
    updated = room_manager.update_room(room_id, occupancy_period)

    if updated:
        return jsonify({"message": "Room occupancy updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update room occupancy"}), 500


# Método para obtener una reserva por su ID
@room_blueprint.route('/room/<room_id>', methods=['GET'])
#@auth_required(groups=["admin"])  # Requiere autenticación y que el usuario pertenezca al grupo "admin"
def get_room_by_id(room_id):
    room = room_manager.get_room_by_id(room_id) 
    if room:
        return jsonify(room.to_dict()), 200
    else:
        return jsonify({"message": "Room not found"}), 404