from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import create_tables
from api import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
    yield

app = FastAPI(title="Student Management API", version="1.0.0", lifespan=lifespan)

app.include_router(router)