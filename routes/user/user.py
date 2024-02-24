from flask import Blueprint, jsonify, make_response, redirect, request, send_file, session, url_for, current_app as app
from pymongo import MongoClient
from models.users import UserManager, User  # Import the User and UserManager classes
from models.room import RoomManager, Room
from models.booking import BookingManager  # Importa el BookingManager
from dotenv import load_dotenv
import os
from flask_mail import Mail, Message
load_dotenv()

# Obtén la cadena de conexión desde la variable de entorno
mongo_uri = os.getenv('MONGO_URI')

# Verifica si la cadena de conexión está presente
if not mongo_uri:
    raise ValueError("La variable de entorno MONGO_URI no está configurada.")

# Crea el cliente de MongoDB
mongo_client = MongoClient(mongo_uri)


user_manager = UserManager(mongo_client, 'hotel', 'users')  # Initialize UserManager
room_manager = RoomManager(mongo_client, 'hotel', 'rooms')

user_blueprint = Blueprint('user_blueprint', __name__)

@user_blueprint.route('/user/test', methods=['GET'])
def test():
    return jsonify({"message": "We are alive"})

#TODO: Manejar errores si no hay conexion a la DB
@user_blueprint.route('/user/create', methods=['POST'])
def create_user():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    # Elimina la referencia a _id cuando creas un nuevo usuario
    new_user = User.from_dict(json_data)
    user_id = user_manager.create_user(new_user.__dict__)

    if user_id:
        return jsonify({"message": "User created successfully", "user_id": str(user_id)}), 201
    else:
        return jsonify({"message": "Failed to create user"}), 500

@user_blueprint.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = user_manager.get_user(user_id)
    if user:
        return jsonify(user.__dict__), 200  # Convert the User object to a dictionary for JSON response
    else:
        return jsonify({"message": "User not found"}), 404

@user_blueprint.route('/rooms/search', methods=['POST'])
def find_rooms():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400
    
    num_people = json_data.get('num_people')
    start_date = json_data.get('start_date')
    end_date = json_data.get('end_date')
    num_rooms = json_data.get('num_rooms')  # Si no se proporciona, por defecto es 3

    if not all([num_people, start_date, end_date]):
        return jsonify({"message": "Missing required parameters (num_people, start_date, end_date)"}), 400

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

###### Rutas para el manejo de reservas ######

booking_manager = BookingManager(mongo_client, 'hotel', 'bookings')  # Inicializa el BookingManager

@user_blueprint.route('/user/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    booking = booking_manager.get_booking_by_id(booking_id)
    if booking:
        return jsonify(booking.to_dict()), 200
    else:
        return jsonify({"message": "Booking not found"}), 404


# @user_blueprint.route('/send_mail', methods=['POST'])
# def send_mail():
#     data = request.json
#     subject = data.get('subject', 'Sin Asunto')
#     recipient = data.get('recipient', None)
#     message = data.get('message', '')

#     if not recipient:
#         return jsonify({'error': 'El destinatario es requerido'}), 400

#     msg = Message(subject, recipients=[recipient])
#     msg.body = message
#     from app import mail
#     app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
#     app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
#     app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
#     app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') 
#     app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
#     app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
#     app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
#     mail.send(msg)

#     return jsonify({'message': 'Correo enviado exitosamente'}), 200