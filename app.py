
from routes.user.user import user_blueprint
from routes.room.room import room_blueprint
from routes.admin.admin import admin_blueprint
from routes.login.auth import auth_blueprint, auth
from flask import Flask
from flask_cors import CORS 
from config import Config
import toml

config = toml.load('./config.toml')
FRONTEND_DOMAIN = config['domains']['frontend_domain']

app = Flask(__name__)
app.config.from_object(Config)
auth.init_app(app) 


CORS(app, origins=[FRONTEND_DOMAIN], supports_credentials=True) 
# Registra los blueprints

app.register_blueprint(user_blueprint)
app.register_blueprint(room_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint)


# Configura CORS para permitir solicitudes desde http://localhost:4200

config = toml.load('./config.toml')
FRONTEND_DOMAIN = config['domains']['frontend_domain']
CORS(app, origins=[FRONTEND_DOMAIN], supports_credentials=True) 

app.run(debug=True, host='0.0.0.0', threaded=True, port=5000)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
