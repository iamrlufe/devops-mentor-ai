from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.teacher import TeacherAgent

app = FastAPI(
    title="DevOps Mentor AI",
    version="0.1.0",
)

teacher = TeacherAgent()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "name": "DevOps Mentor AI",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    answer = teacher.ask(request.message)

    return {
        "answer": answer
    }
