# catalog_service/main.py


import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "Catalog service is running",
        "env": os.getenv("FASTAPI_ENV", "unknown"),
        "db": os.getenv("DATABASE_URL", "not set")
    }
