import os
import logging
import time
import zipfile
import shutil
from utils.server_status import server_status
from label_studio_sdk.client import LabelStudio
from config.config import Config

def label_studio_export_processing_task(id_project_train, id_project_val=None, chunk_size=1024*1024):
    logger = logging.getLogger(__name__)
    
    # Configure file logging
    file_handler = logging.FileHandler('export_progress.log')
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    # Reset server status for export process
    server_status.update({
        "status": "exporting",
        "start_time": time.time(),
        "message": "Starting export process",
        "progress": 0,
        "current_epoch": 0,
        "epoch_progress": 0,
        "end_time": None,
    })

    if id_project_val is None:
        id_project_val = id_project_train

    try:
        # client = LabelStudio(
        #     base_url="http://192.168.18.206:8080",
        #     api_key="ca30878a7b9f2791b849c3353ec462edc94a3082"
        # )
        client = LabelStudio(
            base_url=Config.LABEL_STUDIO_URL,
            api_key=Config.LABEL_STUDIO_API_KEY
        )

        base_dir = os.path.dirname(__file__)
        training_dir = os.path.join(base_dir, "../training")
        os.makedirs(training_dir, exist_ok=True)

        train_export_path = os.path.join(training_dir, "train_export.zip")
        val_export_path = os.path.join(training_dir, "val_export.zip")

        def safe_export(project_id, export_path):
            attempt = 1
            while True:
                try:
                    message = f"Starting export for project {project_id}"
                    logger.info(message)
                    server_status.update({"message": message})
                    export = client.projects.exports.create_export(
                    id=project_id,
                    export_type="YOLO_OBB",
                    download_resources=True,
                    download_all_tasks=True
                    )
                    
                    with open(export_path, 'wb') as f:
                        downloaded_size = 0
                        for chunk in export:
                            if chunk:
                                f.write(chunk)
                                chunk_size = len(chunk)
                                downloaded_size += chunk_size
                                downloaded_mb = downloaded_size/1024/1024
                                message = f"Downloading project {project_id}: {downloaded_mb:.2f} MB"
                                print(f"\rProgress: {message}", end="")  # Show progress in console
                                logger.info(message)
                                server_status.update({
                                    "status": "downloading",
                                    "message": message + f" ({downloaded_mb:.2f} MB)",
                                })
                                print()  # New line after download completes
                    
                    with zipfile.ZipFile(export_path, 'r') as zip_ref:
                     zip_ref.testzip()
                    
                    message = f"Export for project {project_id} completed successfully ({downloaded_mb:.2f} MB)"
                    logger.info(message)
                    server_status.update({"message": message})
                    return export_path

                except Exception as retry_error:
                    message = f"Export attempt {attempt} for project {project_id} failed: {retry_error}"
                    logger.error(message)
                    server_status.update({
                    "message": message,
                    })
                    wait_time = min(2 ** (attempt % 10), 300)
                    time.sleep(wait_time)
                    attempt += 1

        train_zip = safe_export(id_project_train, train_export_path)
        val_zip = safe_export(id_project_val, val_export_path)

        # Update server status on successful completion
        server_status.update({
            "status": "export_complete",
            "end_time": time.time(),
            "message": "Export process completed successfully"
        })

        return train_zip, val_zip

    except Exception as e:
        message = f"Critical export error: {str(e)}"
        logger.error(message)
        server_status.update({
            "status": "export_failed",
            "end_time": time.time(),
            "message": message
        })
        raise RuntimeError(f"Export failed: {str(e)}")