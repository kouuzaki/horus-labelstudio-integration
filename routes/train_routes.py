from flask import Blueprint, jsonify
import threading
from utils.log_handler import log_queue
from utils.training_handler import train_model_subprocess
from utils.server_status import server_status

train_bp = Blueprint("train", __name__)

training_thread = None

@train_bp.route("/", methods=["POST"])
def train():
    global training_thread

    if training_thread is None or not training_thread.is_alive():
        while not log_queue.empty():
            log_queue.get()

        training_thread = threading.Thread(target=train_model_subprocess, args=(log_queue,))
        training_thread.start()

        return jsonify({"message": "Training started successfully", "status": "training"}), 200

    return jsonify({"message": "Training is already in progress", "status": server_status["status"]}), 400
