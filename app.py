from flask import Flask
from flask_cors import CORS
from routes.train_routes import train_bp
from routes.log_routes import logs_bp
from routes.status_routes import status_bp
from routes.model_routes import model_bp


def create_app():
    
    """
    Application factory function to create and configure the Flask app.
    """
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

    app.url_map.strict_slashes = False
    
    @app.route("/", methods=["GET"])
    def home():
        return "Horus Training API is running!"
    
    # Register Blueprints
    app.register_blueprint(train_bp, url_prefix="/train")
    app.register_blueprint(logs_bp, url_prefix="/logs")
    app.register_blueprint(status_bp, url_prefix="/status")
    app.register_blueprint(model_bp, url_prefix="/model")

    return app
