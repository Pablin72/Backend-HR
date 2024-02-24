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


# @admin_blueprint.route("/create_user", methods=["POST"])
# @auth_required(groups=["admin"])
# def create_user():
#     username = request.json["username"]
#     email = request.json["email"]
#     return create_cognito_user(username, email)

# @admin_blueprint.route("/users", methods=["GET"])
# @auth_required(groups=["admin"])
# def get_users_table():
#     return get_all_users()

# @admin_blueprint.route("/delete_user", methods=["DELETE"])
# @auth_required(groups=["admin"])
# def delete_user():
#     if not is_admin(session):
#         return jsonify({"error": "Necesitas ser un administrador"}), 400 
    
#     user_info = session.get("user_info", {})
#     username = user_info.get("cognito:username")

#     deleted_username = request.json["username"]

#     if is_user_admin(deleted_username):
#         return jsonify({"error": "Un administrador no puede eliminar otro administrador"}), 400 

#     if username == deleted_username:
#         return jsonify({"error": "Un usuario no puede eliminarse a si mismo."}), 400 


#     return delete_user_cognito(deleted_username)

@admin_blueprint.route("/disable_user", methods=["PUT"])
@auth_required(groups=["admin"])
def disable_user():
    if not is_admin(session):
        return jsonify({"error": "Necesitas ser un administrador"}), 400 
    
    user_info = session.get("user_info", {})
    username = user_info.get("cognito:username")

    deleted_username = request.json["username"]

    if is_user_admin(deleted_username):
        return jsonify({"error": "Un administrador no puede deshabilitar otro administrador"}), 400 

    if username == deleted_username:
        return jsonify({"error": "Un usuario no puede desahabilitarse a si mismo."}), 400 

    return disable_user_login(deleted_username)

@admin_blueprint.route("/enable_user", methods=["PUT"])
@auth_required(groups=["admin"])
def enable_user():
    username = request.json["username"]
    return enable_user_login(username)

@admin_blueprint.route('/count_aigenerated_files/<username>', methods=['GET'])
@auth_required(groups=["admin"])
def count_aigenerated_files(username):
    
    # Verificar si el username está disponible
    if not username:
        return jsonify({"message": "Username not available"}), 400
    
    prefix = f"library/{username}/"
    
    # Listar objetos en S3 bajo /library/<username>/
    objects = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)

    if 'Contents' not in objects:
        return jsonify({'message': 'No files found'}), 404
    
    # Contar los archivos que contienen "aigenerated" en su nombre
    count = 0
    for obj in objects['Contents']:
        if 'aigenerated' in obj['Key']:
            count += 1
    
    return jsonify({'aigenerated_count': count}), 200  

@admin_blueprint.route('/count_template_files/<username>', methods=['GET'])
@auth_required(groups=["admin"])
def count_template_files(username):
    
    # Verificar si el username está disponible
    if not username:
        return jsonify({"message": "Username not available"}), 400
    
    prefix = f"library/{username}/"
    
    # Listar objetos en S3 bajo /library/<username>/
    objects = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)

    if 'Contents' not in objects:
        return jsonify({'message': 'No files found'}), 404
    
    # Contar los archivos que contienen "aigenerated" en su nombre
    count = 0
    for obj in objects['Contents']:
        if 'template' in obj['Key']:
            count += 1
    
    return jsonify({'template_count': count}), 200  

@admin_blueprint.route('/upload_planning_data', methods=['POST'])
@auth_required(groups=["admin"])
def upload_admin_planning_data():
    # Obtener el nombre de usuario para el cual se está subiendo el archivo
    username_for_upload = request.args.get('username')

    # Verificar si el nombre de usuario está disponible
    if not username_for_upload:
        return jsonify({"error": "Username not provided"}), 400

    # Comprobar si el archivo se ha enviado en la petición
    file = request.files.get('file')
    if file is None:
        return jsonify({"error": "No file provided"}), 400

    # Comprobar el tipo de archivo
    allowed_extensions = ['.csv', '.xlsx']
    file_extension = os.path.splitext(file.filename)[1]
    if file_extension not in allowed_extensions:
        return jsonify({"error": "Invalid file type"}), 400

    # Subir el archivo a S3
    upload_response = upload_planning_data(file, username_for_upload, file_extension)

    if upload_response.get("success"):
        return jsonify({"message": "File uploaded successfully", "url": upload_response["url"]})
    else:
        return jsonify({"error": upload_response.get("error", "Error uploading file")}), 500


@admin_blueprint.route('/get_user_usage/<sub>', methods=['GET'])
@auth_required(groups=["admin"])
def get_user_usage_endpoint(sub):
    user_id = sub

    # Verificar si el user_id está disponible
    if not user_id:
        return jsonify({"message": "User ID not available"}), 400

    detail = request.args.get('detail', 'false').lower() == 'true'

    result = fetch_user_usage(user_id, detail)
    return jsonify(result), 200 if 'message' not in result else 404



##### MANEJO DE RESERVAS #####

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
    

