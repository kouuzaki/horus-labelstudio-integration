import time
import os
import shutil
import zipfile
import subprocess
import traceback
from utils.label_studio_handler import label_studio_export_processing_task
from utils.yolo_parser import parse_yolo_output
from utils.server_status import server_status
from utils.parse_csv_to_json import parse_csv_to_json
from utils.image_processing import image_processing

def train_model_subprocess(log_queue):
    """
    Train YOLO model using subprocess, ensuring the training directory is overwritten for every new training session.
    """
    try:
        # Reset server status
        server_status.update(
            {
                "status": "training",
                "start_time": time.time(),
                "message": "Training started",
                "progress": 0,
                "current_epoch": 0,
                "epoch_progress": 0,
                "end_time": None,
                "realtime_output": {
                    "current_epoch": 0,
                    "total_epochs": 0,
                    "progress": 0,
                    "epoch_progress": 0,
                    "gpu_memory": None,
                    "box_loss": None,
                    "cls_loss": None,
                    "dfl_loss": None,
                    "instances": None,
                    "size": None,
                    "show": False,
                }
            }
        )

        # Step 1: Set up static training directory
        base_dir = os.path.dirname(__file__)  # Get the current script's directory
        training_dir = os.path.join(base_dir, "../training")  # Relative path to training directory
        
        # If the training directory exists, delete it to avoid conflicts
        if os.path.exists(training_dir):
            shutil.rmtree(training_dir)
        os.makedirs(training_dir, exist_ok=True)

        # Step 2: Export data from Label Studio
        export_result = label_studio_export_processing_task()

        # Save the export result to a file
        output_file = os.path.join(training_dir, "export_result.zip")
        with open(output_file, "wb") as f:
            for chunk in export_result:
                f.write(chunk)

        # Extract the exported data
        extract_path = os.path.join(training_dir, "extracted_data")
        with zipfile.ZipFile(output_file, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # Step 3: Read classes.txt
        classes_file_path = os.path.join(extract_path, "classes.txt")
        with open(classes_file_path, "r") as classes_file:
            classes_content = classes_file.read().strip()
            classes = classes_content.split("\n")

        # Step 4: Create YAML file
        yaml_path = os.path.join(training_dir, "data.yaml")
        yaml_content = f"""
        train: {os.path.abspath(extract_path)}/images
        val: {os.path.abspath(extract_path)}/images

        nc: {len(classes)}
        names: ['{"', '".join(classes)}']
        """
        with open(yaml_path, "w") as yaml_file:
            yaml_file.write(yaml_content)

        # Debug: Log YAML file location
        print(f"YAML file created at: {yaml_path}")

        # Step 5: Prepare training command
        train_command = [
            "yolo", "train", 
            f"data={yaml_path}", 
            f"model={os.path.abspath(os.path.join(base_dir, '../model/yolov8n.pt'))}",
            "epochs=10", 
            "lr0=0.01",
            "patience=2",
            "device=cuda:0",
            "batch=128",
        ]

        # Step 6: Start subprocess for training
        process = subprocess.Popen(
            train_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=training_dir,  # Run the subprocess in the training directory
            bufsize=1,
            universal_newlines=True,
        )

        # Step 7: Process real-time output
        for line in iter(process.stdout.readline, ''):
            # Add line to log queue
            log_queue.put(line.strip())

            # Parse line for progress
            parsed_data = parse_yolo_output(line.strip())
            if parsed_data:
                
                print(parsed_data)
                # Update total epochs detected
                if parsed_data.get("status") == "total_epochs_detected":
                    server_status["total_epochs"] = parsed_data["total_epochs"]
                    
                
                # Update progress and epoch details
                if parsed_data.get("show"):
                    server_status.update({
                        "progress": parsed_data["progress"],
                        "current_epoch": parsed_data["current_epoch"],
                        "total_epochs": parsed_data.get("total_epochs", server_status["total_epochs"]),
                        "realtime_output": parsed_data,
                    })

                print('Server Status', server_status) 

        # Wait for process to complete
        process.stdout.close()
        return_code = process.wait()
                
        if return_code == 0:
            # Parse the CSV file to JSON
            csv_file = os.path.join(training_dir, "runs/detect/train", "results.csv")
            json_output = parse_csv_to_json(csv_file)
            
            # Save the JSON output
            with open(os.path.join(training_dir, "runs/detect/train", "results.json"), "w") as json_file:
                json_file.write(json_output)
            
            print('Json file created', json_output)
            
            
            # # Process images
            image_processing(training_dir, json_output)        
        
        else:
            # Update status after failed training
            server_status.update({
            "status": "error",
            "end_time": time.time(),
            "progress": 100,
            "current_epoch": server_status["current_epoch"],
            "message": "Training failed",
            })

    except Exception as e:
        error_msg = f"Training Error: {str(e)}\n{traceback.format_exc()}"
        server_status.update(
            {
                "status": "error",
                "message": str(e),
            }
        )
        log_queue.put(error_msg)
