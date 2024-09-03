from services.sql_app import crud, models, schemas
from fastapi.middleware.cors import CORSMiddleware
from services.sql_app.database import SessionLocal, engine
from dotenv import load_dotenv
from fastapi import FastAPI


load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)
