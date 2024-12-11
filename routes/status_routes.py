from flask import Blueprint, jsonify
from utils.server_status import server_status

status_bp = Blueprint("status", __name__)

@status_bp.route("/", methods=["GET"])
def get_status():
    
    return jsonify(server_status)
