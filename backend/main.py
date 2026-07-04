from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from .db import engine
from .schemas import UserSubmission


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Psygraph backend is running normally"}


@app.post("/submit")
def submit_answers(payload: UserSubmission):
    print(f"Received data for user: {payload.user_id}")

    return {"status": "success", "data_received": payload}
