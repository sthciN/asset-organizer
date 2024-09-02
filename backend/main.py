from app import app
from fastapi import HTTPException
from services.process.provider import png_provider


@app.get("/")
def read_root():
    return {"Healthcheck": "OK"}

# TODO POST method
@app.get("/process-pngs")
def process_pngs():
    try:
        png_provider()
    
    except HTTPException as error:
        raise error
    
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    return {"detail": {"message": "Success"}}
