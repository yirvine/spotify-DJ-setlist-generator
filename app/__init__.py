# from flask import Flask
# from flask_session import Session
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os

# def create_app():
#     load_dotenv()
#     app = Flask(__name__)
#     app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
#     app.config['SESSION_TYPE'] = 'filesystem'  # Use server-side sessions
#     app.config['SESSION_PERMANENT'] = False
#     app.config['SESSION_USE_SIGNER'] = True
#     app.config['SESSION_KEY_PREFIX'] = 'dj_set_'  # Prefix for session keys
#     app.config['SESSION_FILE_DIR'] = os.getenv('SESSION_FILE_DIR', './flask_session')

#     Session(app)  # Initialize server-side session
#     CORS(app)  # Enable CORS for all routes

#     from . import routes
#     app.register_blueprint(routes.bp)

#     return app

# print(f"FLASK_SECRET_KEY: {os.getenv('FLASK_SECRET_KEY')}")

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

    CORS(app)  # Enable CORS for all routes

    from . import routes
    app.register_blueprint(routes.bp)

    return app

print(f"FLASK_SECRET_KEY: {os.getenv('FLASK_SECRET_KEY')}")
