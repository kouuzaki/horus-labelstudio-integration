from label_studio_sdk.client import LabelStudio

def label_studio_export_processing_task():
    client = LabelStudio(
        base_url="http://localhost:8081",
        api_key="796f1931797c376857b3c3bba4b306797cba1606",
    )
    return client.projects.exports.create_export(
        id=1,
        export_type="YOLO_OBB",
        download_all_tasks=True,
        download_resources=True,
        ids=1,
    )
