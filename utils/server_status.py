server_status = {
    "status": "idle",
    "progress": 0,
    "current_epoch": 0,
    "total_epochs": 0,
    "message": "",
    "start_time": 0,
    "end_time": 0,
    "realtime_output": [
        {
            "current_epoch": 0,
            "total_epochs": 0,
            "progress": 0,
            "epoch_progress": 0,
            "gpu_memory": 0,
            "box_loss": 0,
            "cls_loss": 0,
            "dfl_loss": 0,
            "instances": 0,
            "size": 0,
            "show": False
        }    
    ],
    "training_results": {
        "status": "idle",  # Status training, default idle
        "progress": 0,  # Progress bar (0-100)
        "total_epochs": 0,  # Total epoch yang dijalankan
        "training_time_seconds": 0.0,  # Total waktu training
        "best_epoch": {
            "epoch": 0,
            "metrics/mAP50-95(B)": 0.0,
            "metrics/mAP50(B)": 0.0,
            "train_loss": {
                "box_loss": 0.0,
                "cls_loss": 0.0,
                "dfl_loss": 0.0
            },
            "validation_loss": {
                "box_loss": 0.0,
                "cls_loss": 0.0,
                "dfl_loss": 0.0
            }
        },
        "images": {
          "results": '',
           "confusion_matrix": '',
           "labels_cerrelogram": '',
           "precision_recall_curve": '',
           "precision_curve": '',
           "labels": '',
           "f1_curve": '',
        }
    } 
}
