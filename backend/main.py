import os
import uuid
from app import app
from typing import Dict
from fastapi import HTTPException, BackgroundTasks
from services.process.provider import png_provider, task_statuses
from services.google.drive import GoogleDrive

@app.get("/")
def health():
    return {"Healthcheck": "OK"}

@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    if task_id not in task_statuses:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"detail": {"task_id": task_id, "status": task_statuses[task_id]}}

@app.get("/file-list")
def read_drive():
    folder_id = os.environ.get('PNG_FOLDER_ID')
    file_list = GoogleDrive().fetch_png_list(folder_id)
    return {"detail": [f['name'] for f in file_list]}

@app.post("/api/process-pngs")
def process_pngs():
    try:
        png_provider()
    
    except HTTPException as error:
        raise error
    
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    return {"detail": {"message": "Success"}}

@app.post("/api/process-pngs-background")
async def process_pngs_background(background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(png_provider, task_id)
    return {"detail": {"message": "In progress", "task_id": task_id}}
