from utils.server_status import server_status
import os
import base64
import json
import time

def training_result_processing(training_dir, json_output):
    # Image directory
    image_dir = os.path.join(training_dir, "runs/detect/train")
    model_path = os.path.join(training_dir, "runs/detect/train/weights/best.pt")
    
    # Define the list of images to be processed
    image_files = {
        "results": "results.png",
        "confusion_matrix": "confusion_matrix.png",
        "labels_cerrelogram": "labels_correlogram.jpg",
        "precision_recall_curve": "PR_curve.png",
        "precision_curve": "P_curve.png",
        "labels": "labels.jpg",
        "f1_curve": "F1_curve.png"
    }
    
    # Store images in base64 format
    images_base64 = {}

    # Iterate over the list of registered images
    for key, file_name in image_files.items():
        file_path = os.path.join(image_dir, file_name)
        # Check if the file exists
        if os.path.exists(file_path):
            # Read and convert image to base64
            with open(file_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                images_base64[key] = img_data
        else:
            # If the file is not found, add None or an error message
            images_base64[key] = None
            


    # Parse training results into the desired format
    # Load the JSON output and update it with additional properties
    training_results = json.loads(json_output)
    training_results["model"] = {}
    training_results.update({
        "status": "completed",
        "progress": 100,
        "total_epochs": server_status["total_epochs"],
        "training_time_seconds": time.time() - server_status["start_time"],
        "images": images_base64  # Store processed images
    })

    if os.path.exists(model_path):
        try:
            model_size = os.path.getsize(model_path)
            training_results["model"].update({
                "name": os.path.basename(model_path),
                "path": model_path,
                "size_bytes": model_size,
                "available": True
            })
        except Exception as e:
            training_results["model"].update({
                "error": str(e)
            })
    

    # Update status after training is completed
    server_status.update({
        "status": "completed", 
        "end_time": time.time(),
        "progress": 100,
        "current_epoch": server_status["current_epoch"],
        "message": "Training completed successfully",
        "training_results": training_results,
    })
    
    return server_status, training_results
