from label_studio_sdk.client import LabelStudio

def label_studio_export_processing_task():
    client = LabelStudio(
        base_url="http://192.168.18.206:8080",
        api_key="ca30878a7b9f2791b849c3353ec462edc94a3082",
        
    )
    # return client.projects.exports.create_export(
    #     id=79,
    #     export_type="YOLO_OBB",
    #     download_all_tasks=True,
    #     download_resources=True,
    #     ids=68,
    
    return client.projects.get(79)

data = label_studio_export_processing_task()
print(data)
# for export_data in data:
#     print(export_data)
#     # If you want to save the export data
#     if hasattr(export_data, 'download_url'):
#         print(f"Download URL: {export_data.download_url}")