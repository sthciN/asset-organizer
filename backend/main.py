from app import app
from services.process.provider import png_provider


@app.get("/")
def read_root():
    return {"Healthcheck": "OK"}

@app.get("/def-endpoint")
def test_endpoint():
    png_provider()
    return 'ok'

    