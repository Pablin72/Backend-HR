from dotenv import load_dotenv
from os import environ, path, urandom
# Load variables from .env
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = environ.get("SECRET_KEY", urandom(32))
    FLASK_APP = "TEST_APP"
    FLASK_ENV = "TESTING"

    # Cognito config
    # # AWS_COGNITO_DISABLED = True  # Can set to turn off auth (e.g. for local testing)
    AWS_REGION = environ["AWS_REGION"]
    AWS_COGNITO_USER_POOL_ID = environ["AWS_COGNITO_USER_POOL_ID"]
    AWS_COGNITO_DOMAIN = environ["AWS_COGNITO_DOMAIN"]
    AWS_COGNITO_USER_POOL_CLIENT_ID = environ["AWS_COGNITO_USER_POOL_CLIENT_ID"]
    AWS_COGNITO_USER_POOL_CLIENT_SECRET = environ["AWS_COGNITO_USER_POOL_CLIENT_SECRET"]
    AWS_COGNITO_REDIRECT_URL = environ["AWS_COGNITO_REDIRECT_URL"]
    AWS_COGNITO_LOGOUT_URL = environ["AWS_COGNITO_LOGOUT_URL"]
    AWS_COGNITO_COOKIE_AGE_SECONDS = environ["AWS_COGNITO_COOKIE_AGE_SECONDS"]
    AWS_COGNITO_COOKIE_DOMAIN = environ["AWS_COGNITO_COOKIE_DOMAIN"]
    AWS_COGNITO_COOKIE_SAMESITE = environ["AWS_COGNITO_COOKIE_SAMESITE"]
    MAIL_USERNAME=environ["MAIL_USERNAME"]
    MAIL_PASSWORD=environ["MAIL_PASSWORD"]
    MAIL_PORT=environ["MAIL_PORT"]
    MAIL_SERVER=environ["MAIL_SERVER"]
    MAIL_USE_TLS=environ["MAIL_USE_TLS"]
    MAIL_USE_SSL=environ["MAIL_USE_SSL"]
    MAIL_DEFAULT_SENDER =environ["MAIL_DEFAULT_SENDER"]
