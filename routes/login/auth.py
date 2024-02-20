# auth_blueprint.py
from flask import Blueprint, redirect, url_for, session, jsonify, request
from flask_cognito_lib import CognitoAuth
from flask_cognito_lib.decorators import cognito_login, cognito_login_callback, cognito_logout, auth_required
from flask_cognito_lib.exceptions import AuthorisationRequiredError, CognitoGroupRequiredError
import toml

config = toml.load('./config.toml')
ADMIN_HOME_VIEW = config['views']['admin_view']
USER_HOME_VIEW = config['views']['user_view']

auth_blueprint = Blueprint('auth_blueprint', __name__)
auth = CognitoAuth()

def is_admin(response_json):
    """ This function verify if an user is part of the admin cognito:groups

    Args:
        response_json (json): The claim of the JWT of a user

    Returns:
        Boolean: True if the user is part of the cognito:groups admin, otherwise False.
    """
    try:
        # Verificar si 'admin' está en alguna de las listas de 'cognito:groups'
        for key in ['claims', 'user_info']:
            if key in response_json and 'cognito:groups' in response_json[key]:
                if 'admin' in response_json[key]['cognito:groups']:
                    return True
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    


@auth_blueprint.route("/")
def home():
    return "Hello World"

@auth_blueprint.app_errorhandler(AuthorisationRequiredError)
def auth_error_handler(err):
    # Register an error handler if the user hits an "@auth_required" route
    # but is not logged in to redirect them to the Cognito UI
    return redirect(url_for("auth_blueprint.login"))

@auth_blueprint.app_errorhandler(CognitoGroupRequiredError)
def missing_group_error_handler(err):
    # Register an error handler if the user hits an "@auth_required" route
    # but is not in all of groups specified
    return jsonify("Group membership does not allow access to this resource"), 403


# Aquí van todos los endpoints relacionados con la autenticación
@auth_blueprint.route("/login")
@cognito_login
def login():
    next_url = request.args.get('next', '')
    if next_url:
        session['next'] = next_url

@auth_blueprint.route("/postlogin")
@cognito_login_callback
def postlogin():
    next_url = session.pop('next', None)
    if next_url:
        return redirect(next_url)

    if is_admin(session):
        return redirect(ADMIN_HOME_VIEW)
    else:
        return redirect(USER_HOME_VIEW)

@auth_blueprint.route("/claims")
@auth_required()
def claims():
    return jsonify(dict(session))

@auth_blueprint.route("/logout")
@cognito_logout
def logout():
    #La logica la maneja el decorador
    pass

@auth_blueprint.route("/postlogout")
def postlogout():
    return redirect(url_for("auth_blueprint.home"))

