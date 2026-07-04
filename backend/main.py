from fastapi import FastAPI
from schemas import UserSubmission

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Psygraph backend is running normally"}


@app.post("/submit")
def submit_answers(payload: UserSubmission):
    print(f"Received data for user: {payload.user_id}")

    return {"status": "success", "data_received": payload}
