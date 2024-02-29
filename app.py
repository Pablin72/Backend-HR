
from routes.user.user import user_blueprint
from routes.room.room import room_blueprint
from routes.admin.admin import admin_blueprint
from routes.login.auth import auth_blueprint, auth
from flask import Flask, jsonify, request
from flask_cors import CORS 
from config import Config
import toml
from dotenv import load_dotenv
from flask_mail import Mail, Message
load_dotenv()
config = toml.load('./config.toml')
FRONTEND_DOMAIN = config['domains']['frontend_domain']
import os
app = Flask(__name__)
# Cargando configuraciones directamente desde variables de entorno
# Configuración explícita para Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'hotelcopodenieve3@gmail.com'
app.config['MAIL_PASSWORD'] = 'qteq endd ssms dqss'
app.config['MAIL_DEFAULT_SENDER'] = 'hotelcopodenieve3@gmail.com'

app.config.from_object(Config)
# Configuración explícita para Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'hotelcopodenieve3@gmail.com'
app.config['MAIL_PASSWORD'] = 'qteq endd ssms dqss'
app.config['MAIL_DEFAULT_SENDER'] = 'hotelcopodenieve3@gmail.com'
auth.init_app(app) 
# Configuración adicional para Flask-Mail
load_dotenv()
# Inicializar Flask-Mail
mail = Mail(app)

auth.init_app(app)

CORS(app, origins=[FRONTEND_DOMAIN], supports_credentials=True)

# Registra los blueprints
app.register_blueprint(user_blueprint)
app.register_blueprint(room_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)

@app.route('/send_email', methods=['POST'])
def send_email():
    # Obtener los datos del cuerpo de la solicitud, que debe ser un JSON
    
    data = request.get_json()

    # Asegurarse de que los datos necesarios estén presentes
    if not data or 'recipient' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({'error': 'Missing data'}), 400

    subject = data['subject']
    recipient = data['recipient']
    body = data['body']

    # Crear el mensaje
    msg = Message(subject, recipients=[recipient], body=body, sender=app.config['MAIL_DEFAULT_SENDER'])

    # Intentar enviar el correo
    try:
        mail.send(msg)
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        # En caso de cualquier excepción, enviar una respuesta de error
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', threaded=True, port=5000)