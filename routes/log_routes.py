from flask import Blueprint, Response, jsonify
from utils.log_handler import log_queue
from utils.server_status import server_status
import queue

logs_bp = Blueprint("logs", __name__)
stored_logs = []  # Untuk menyimpan history log

@logs_bp.route("/", methods=["GET"])
def stream_logs():
    """
    Stream logs using SSE (Server-Sent Events).
    """
    def generate():
        # Kirim log yang tersimpan terlebih dahulu
        for log in stored_logs:
            yield f"data: {log}\n\n"
            
        while True:
            try:
                log = log_queue.get(timeout=1)
                stored_logs.append(log)  # Simpan log baru
                yield f"data: {log}\n\n"
            except queue.Empty:
                if server_status["status"] in ["completed", "error"]:
                    break

    return Response(generate(), content_type="text/event-stream")

