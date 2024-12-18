import json
import logging
import os
import shutil
import subprocess
import time
import traceback
import zipfile

from utils.label_studio_handler import label_studio_export_processing_task
from utils.parse_csv_to_json import parse_csv_to_json
from utils.project_task_extractor import extract_project_tasks
from utils.server_status import server_status
from utils.training_result_processing import training_result_processing
from utils.yolo_parser import parse_yolo_output


def train_model_subprocess(log_queue, id_project_train, id_project_val, labels):
    """
    Train YOLO model using subprocess, ensuring the training directory is overwritten for every new training session.
    """
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    
    try:
        # Reset server status
        server_status.update(
            {
                "start_time": time.time(),
                "progress": 0,
                "current_epoch": 0,
                "epoch_progress": 0,
                "end_time": None,
                "realtime_output": [],
            }
        )

        # Step 1: Set up static training directory
        root_dir = os.getcwd()
        training_dir = os.path.join(root_dir, "training")  # Relative path to training directory

        # If the training directory exists, delete it to avoid conflicts
        if os.path.exists(training_dir):
            shutil.rmtree(training_dir)
            os.makedirs(training_dir, exist_ok=True)

       # Step 2: Export data from Label Studio with train and val projects
        try:            
            # Check if id_project_train or id_project_val is empty
            if not id_project_train or not id_project_val:
                error_message = "Both id_project_train and id_project_val must be provided."
                if not id_project_train:
                    error_message = "id_project_train is missing."
                if not id_project_val:
                    error_message = "id_project_val is missing."
                
                server_status.update(
                    {
                        "status": "error",
                        "message": error_message,
                    }
                )
                log_queue.put(error_message)
                return
            
            train_extract_path = os.path.join(training_dir, "train_extracted")
            val_extract_path = os.path.join(training_dir, "val_extracted")
            
            os.makedirs(train_extract_path, exist_ok=True)
            os.makedirs(val_extract_path, exist_ok=True)
            
            # Extract train data
            extract_project_tasks(project_id=id_project_train, labels=labels, extract_path=train_extract_path)
            logger.info(f"Extracted train data to: {train_extract_path}")
            
            # Extract val data
            extract_project_tasks(project_id=id_project_val, labels=labels, extract_path=val_extract_path)
            logger.info(f"Extracted val data to: {val_extract_path}")

        except Exception as e:
            logger.error(f"Error during data export and extraction: {str(e)}")
            raise

        # Step 3: Read classes.txt from both train and validation exports
        def read_classes_from_export(export_path):
            """
            Read classes from classes.txt in the export path.
            
            Args:
                export_path (str): Path to the extracted export directory
            
            Returns:
                list: List of classes found in classes.txt
            """
            classes_file_path = os.path.join(export_path, "classes.txt")
            
            if not os.path.exists(classes_file_path):
                logger.warning(f"classes.txt not found in {export_path}")
                return []
            
            with open(classes_file_path, "r") as classes_file:
                classes_content = classes_file.read().strip()
                return [cls.strip() for cls in classes_content.split("\n") if cls.strip()]

        # Combine and deduplicate classes from both train and val exports
        train_classes = read_classes_from_export(train_extract_path)
        val_classes = read_classes_from_export(val_extract_path)

        # Combine and remove duplicates while preserving order
        classes = list(dict.fromkeys(train_classes + val_classes))

        logger.info(f"Detected classes from both train and val: {classes}")

        # Validate that classes are consistent between train and val
        if set(train_classes) != set(val_classes):
            logger.warning("Classes differ between train and validation datasets!")
            logger.warning(f"Train classes: {train_classes}")
            logger.warning(f"Validation classes: {val_classes}")
            
        
        # Step 4: Create YAML file
        yaml_path = os.path.join(training_dir, "data.yaml")
        # Create yaml content with proper formatting
        names_dict = {i: name for i, name in enumerate(classes)}
        yaml_content = (
            f"train: {os.path.abspath(train_extract_path)}\n"
            f"val: {os.path.abspath(val_extract_path)}\n\n"
            f"nc: {len(classes)}\n"
            f"names: {names_dict}"
        )
        with open(yaml_path, "w") as yaml_file:
            yaml_file.write(yaml_content)
            
        # Debug: Log YAML file location
        print(f"YAML file created at: {yaml_path}")

        # Step 5: Prepare training command
        train_command = [
            "yolo",
            "train",
            f"data={yaml_path}",
            f"model={os.path.abspath(os.path.join(root_dir, 'model','yolov8n.pt'))}",
            "epochs=100",
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
        try:
            for line in iter(process.stdout.readline, ""):
                # Add line to log queue
                line = line.strip()  # Clean the line
                log_queue.put(line)

                # Parse line for progress
                parsed_data = parse_yolo_output(line)
                if parsed_data:
                    print(parsed_data)  # Debug: Print parsed data

                    # Update total epochs detected
                    if parsed_data.get("status") == "total_epochs_detected":
                        server_status["total_epochs"] = parsed_data["total_epochs"]

                    # Update progress and epoch details
                    if parsed_data.get("show"):
                        current_epoch = parsed_data["current_epoch"]

                        # Get current realtime_output or initialize an empty list
                        realtime_output = server_status.get("realtime_output", [])
                        if len(realtime_output) >= 100:  # Limit array size
                            realtime_output = realtime_output[-99:]  # Keep last 99 entries

                        # Remove any existing entries for the current epoch
                        realtime_output = [
                            entry
                            for entry in realtime_output
                            if entry["current_epoch"] != current_epoch
                        ]

                        # Add the new data for this epoch with timestamp
                        parsed_data["timestamp"] = time.time()

                        # Update realtime output list with the new data
                        realtime_output.append(parsed_data)
                        
                        server_status.update(
                            {
                                "status": "training",
                                "message": "Training in progress",
                                "progress": parsed_data["progress"],
                                "current_epoch": current_epoch,
                                "total_epochs": parsed_data.get(
                                    "total_epochs", server_status.get("total_epochs", 0)
                                ),
                                "epoch_progress": parsed_data.get("epoch_progress", 0),
                                "gpu_memory": parsed_data.get("gpu_memory", 0),
                                "box_loss": parsed_data.get("box_loss", 0),
                                "cls_loss": parsed_data.get("cls_loss", 0),
                                "dfl_loss": parsed_data.get("dfl_loss", 0),
                                "instances": parsed_data.get("instances", 0),
                                "size": parsed_data.get("size", 0),
                                "realtime_output": realtime_output,
                            }
                        )

                        # Save the server status to a JSON file
                        status_json_path = os.path.join(training_dir, "server_status.json")
                        with open(status_json_path, "w") as status_json_file:
                            json.dump(server_status, status_json_file, indent=4)

            # Wait for process to complete
            process.stdout.close()
            return_code = process.wait()

            if return_code == 0:
                # Parse the CSV file to JSON
                csv_file = os.path.join(
                    training_dir, "runs/detect/train", "results.csv"
                )
                json_output = parse_csv_to_json(csv_file)

                # Save the JSON output
                results_json_path = os.path.join(
                    training_dir, "runs/detect/train", "results.json"
                )
                with open(results_json_path, "w") as json_file:
                    json_file.write(json_output)

                # Process training results
                training_result_processing(training_dir, json_output)

            else:
                # Update status after failed training
                server_status.update(
                    {
                        "status": "error",
                        "end_time": time.time(),
                        "progress": 100,
                        "current_epoch": server_status.get("current_epoch", 0),
                        "message": "Training failed",
                    }
                )
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise RuntimeError(f"Training failed unexpectedly: {e}")

    except Exception as e:
        error_msg = f"Training Error: {str(e)}\n{traceback.format_exc()}"
        server_status.update(
            {
                "status": "error",
                "message": str(e),
            }
        )
        log_queue.put(error_msg)
