import logging
from app import create_app
from config import Config


def run_server():
    """
    Function to run the Flask server.
    """
    app = create_app()
    logging.info(f"Starting server on port {Config.PORT}")
    app.run(debug=Config.DEBUG, use_reloader=False, host=Config.HOST, port=Config.PORT)

if __name__ == "__main__":
    run_server()