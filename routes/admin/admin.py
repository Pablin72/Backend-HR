from flask import Blueprint, redirect, request, jsonify, session, url_for
from flask_cognito_lib.decorators import auth_required
from pymongo import MongoClient
from os import environ
from flask_cognito_lib.exceptions import AuthorisationRequiredError, CognitoGroupRequiredError

from models.booking import BookingManager  # Importa el BookingManager
from models.booking import Booking

from dotenv import load_dotenv
import os

admin_blueprint = Blueprint('admin_blueprint', __name__)

@admin_blueprint.app_errorhandler(AuthorisationRequiredError)
def auth_error_handler(err):
    session['next'] = request.url
    return redirect(url_for("auth_blueprint.login"))

@admin_blueprint.app_errorhandler(CognitoGroupRequiredError)
def missing_group_error_handler(err):
    # Register an error handler if the user hits an "@auth_required" route
    # but is not in all of groups specified
    return jsonify("Group membership does not allow access to this resource"), 403

load_dotenv()

# Obtén la cadena de conexión desde la variable de entorno
mongo_uri = os.getenv('MONGO_URI')

# Verifica si la cadena de conexión está presente
if not mongo_uri:
    raise ValueError("La variable de entorno MONGO_URI no está configurada.")

# Crea el cliente de MongoDB
mongo_client = MongoClient(mongo_uri)

booking_manager = BookingManager(mongo_client, 'hotel', 'bookings')  # Inicializa el BookingManager


# Método para obtener todas las reservas
@admin_blueprint.route('/admin/bookings', methods=['GET'])
#@auth_required(groups=["admin"])  # Requiere autenticación y que el usuario pertenezca al grupo "admin"
def get_all_bookings():
    bookings = booking_manager.get_bookings()
    bookings_json = [booking.to_dict() for booking in bookings]  # Convierte cada objeto Booking a dict
    return jsonify(bookings_json), 200

# Método para obtener una reserva por su ID
@admin_blueprint.route('/admin/bookings/<booking_id>', methods=['GET'])
#@auth_required(groups=["admin"])  # Requiere autenticación y que el usuario pertenezca al grupo "admin"
def get_booking_by_id(booking_id):
    booking = booking_manager.get_booking_by_id(booking_id)
    if booking:
        return jsonify(booking.to_dict()), 200
    else:
        return jsonify({"message": "Booking not found"}), 404

# Método para crear una nueva reserva
@admin_blueprint.route('/admin/bookings', methods=['POST'])
#@auth_required(groups=["admin"])  # Requiere autenticación y que el usuario pertenezca al grupo "admin"
def create_booking():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    new_booking = Booking.from_dict(json_data)
    booking_id = booking_manager.write_booking(new_booking)

    if booking_id:
        return jsonify({"message": "Booking created successfully", "booking_id": str(booking_id)}), 201
    else:
        return jsonify({"message": "Failed to create booking"}), 500

# Método para actualizar una reserva existente
@admin_blueprint.route('/admin/bookings/<booking_id>', methods=['PUT'])
#@auth_required(groups=["admin"])  # Requiere autenticación y que el usuario pertenezca al grupo "admin"
def update_booking(booking_id):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    # Crear un objeto Booking a partir de los datos JSON recibidos
    updated_booking = Booking.from_dict(json_data)
    
    # Llamar al método update_booking de booking_manager con el objeto Booking actualizado
    modified_count = booking_manager.update_booking(booking_id, updated_booking)

    if modified_count:
        return jsonify({"message": "Booking updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update booking"}), 500

# Método para eliminar una reserva
@admin_blueprint.route('/admin/bookings/<booking_id>', methods=['DELETE'])
#@auth_required(groups=["admin"])  # Requiere autenticación y que el usuario pertenezca al grupo "admin"
def delete_booking(booking_id):
    deleted_count = booking_manager.delete_booking(booking_id)
    if deleted_count:
        return jsonify({"message": "Booking deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete booking"}), 500
    

