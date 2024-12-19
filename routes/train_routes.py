from flask import Blueprint, jsonify, request
import threading
from label_studio_sdk.client import LabelStudio
from config.config import Config
from utils.log_handler import log_queue
from utils.training_handler import train_model_subprocess
from utils.server_status import server_status

train_bp = Blueprint("train", __name__)

training_thread = None

@train_bp.route("/", methods=["POST"])
def train():
    global training_thread
    try:
        data = request.get_json()
        id_project_train = data.get('id_project_train')
        id_project_val = data.get('id_project_val')

        if training_thread is None or not training_thread.is_alive():
            while not log_queue.empty():
                log_queue.get()

            ls_client = LabelStudio(base_url=Config.LABEL_STUDIO_URL, api_key=Config.LABEL_STUDIO_API_KEY)
            project_detail = ls_client.projects.get(id=id_project_train)
            label_list = project_detail.parsed_label_config.get("label").get("labels")

            training_thread = threading.Thread(target=train_model_subprocess, args=(log_queue, id_project_train, id_project_val, label_list))
            training_thread.start()

            return jsonify({"message": "Training started successfully", "status": "training"}), 200

        return jsonify({"message": "Training is already in progress", "status": server_status["status"]}), 400
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500