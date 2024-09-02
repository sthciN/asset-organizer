from services.sql_app import crud, models, schemas
from services.sql_app.database import SessionLocal, engine
from dotenv import load_dotenv
from fastapi import FastAPI


load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
