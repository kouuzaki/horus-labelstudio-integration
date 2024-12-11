import csv
import json

def parse_csv_to_json(csv_file):
    with open(csv_file, 'r') as csvFile:
        fieldNames = [
            "epoch", "time", "train/box_loss", "train/cls_loss", "train/dfl_loss", 
            "metrics/precision(B)", "metrics/recall(B)", "metrics/mAP50(B)", 
            "metrics/mAP50-95(B)", "val/box_loss", "val/cls_loss", "val/dfl_loss", 
            "lr/pg0", "lr/pg1", "lr/pg2"
        ]
        reader = csv.DictReader(csvFile, fieldNames)
        rows = list(reader)[1:]  # Skip header row
        
        # Find the best epoch based on the highest "metrics/mAP50-95(B)"
        best_epoch = max(rows, key=lambda x: float(x["metrics/mAP50-95(B)"]))
        
        # Format the output
        result = {
            "status": "completed",
            "progress": 100,
            "total_epochs": len(rows),
            "training_time_seconds": sum(float(row["time"]) for row in rows),  # Sum all time
            "best_epoch": {
            "epoch": int(best_epoch["epoch"]),
            "metrics/mAP50-95(B)": float(best_epoch["metrics/mAP50-95(B)"]),
            "metrics/mAP50(B)": float(best_epoch["metrics/mAP50(B)"]),
            "train_loss": {
                "box_loss": float(best_epoch["train/box_loss"]),
                "cls_loss": float(best_epoch["train/cls_loss"]),
                "dfl_loss": float(best_epoch["train/dfl_loss"])
            },
            "validation_loss": {
                "box_loss": float(best_epoch["val/box_loss"]),
                "cls_loss": float(best_epoch["val/cls_loss"]),
                "dfl_loss": float(best_epoch["val/dfl_loss"])
            }
            }
        }
        return json.dumps(result, indent=4)
