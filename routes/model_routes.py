from flask import Blueprint, jsonify, send_file
from utils.server_status import server_status
import os

model_bp = Blueprint("model", __name__)

@model_bp.route("/download", methods=["GET"])
def download_model():
    # Path ke file model
    base_dir = os.path.dirname(__file__)  # Get the current script's directory
    
    training_dir = os.path.join(
            base_dir, "../training"
    )  # Relative path to training directory
    model_path = os.path.join(training_dir, "runs/detect/train/weights/best.pt")
    
    # Cek apakah file model ada
    if not os.path.exists(model_path):
        return jsonify({
            "error": "Model file not found",
            "status": 404
        }), 404
    
    try:
      # Send the model file for download
        return send_file(
            model_path,
            as_attachment=True,
            download_name="best.pt",
            mimetype="application/octet-stream"
        )
    except Exception as e:
        return jsonify({
            "error": f"Error downloading model file: {str(e)}",
            "status": 500
        }), 500