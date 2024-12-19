import os
import time

import psycopg2

from config.config import Config
from utils.server_status import server_status

db_connection = psycopg2.connect(
  database=Config.LABEL_STUDIO_DB_NAME, 
  user=Config.LABEL_STUDIO_DB_USERNAME, 
  password=Config.LABEL_STUDIO_DB_PASSWORD, 
  host=Config.LABEL_STUDIO_DB_HOSTNAME, 
  port=Config.LABEL_STUDIO_DB_PORT
)

db_connection_cursor = db_connection.cursor()

def extract_project_tasks(project_id, labels, extract_path): 
  server_status.update({"status": "extracting", "message": f"Extracting project.."})
  try:
    str_query = f"""
    SELECT
      t.id AS task_id,
      REPLACE(CAST(t.data->'image' AS VARCHAR), 'data/', 'home/nauchara/app/label-studio/mydata/media/') AS image_path,
      tc.result AS annotations
    FROM 
      task t 
    INNER JOIN 
      task_completion tc ON t.id = tc.task_id
    WHERE 
      t.project_id = {project_id}
    """

    db_connection_cursor.execute(str_query)
    task_list = db_connection_cursor.fetchall()

    task_num = 1
    for task in task_list:
      server_status.update({"status": "extracting", "message": f"Extracting task {task_num} of {len(task_list)}"})

      task_id = task[0]
      image_path = task[1]
      annotations = task[2]

      normalized_annotations = ""
      for annotation in annotations:
        x = (annotation["value"]["x"] + (annotation["value"]["width"]/2))/100
        y = (annotation["value"]["y"] + (annotation["value"]["height"]/2))/100
        width = annotation["value"]["width"]/100
        height = annotation["value"]["height"]/100
        normalized_annotations = f"{normalized_annotations} {labels.index(annotation['value']['rectanglelabels'][0])} {x} {y} {width} {height} \r"

      task_label_file = open(f"{extract_path}/labels/{task_id}.txt", "w")
      task_label_file.write(normalized_annotations)
      task_label_file.close()

      os.system(f"cp {image_path} {extract_path}/images/{task_id}.jpg")

      task_num += 1
    
    with open(os.path.join(extract_path, "classes.txt"), "w") as f:
      f.write("\n".join(labels))

    server_status.update(
      {
        "status": "export_complete", 
        "end_time": time.time(),
        "message": "Export process completed successfully",
      }
    )
    return True
  except Exception as e:
    server_status.update({"status": "error", "message": str(e)})