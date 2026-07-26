from fastapi import FastAPI

app = FastAPI(
    title="DevOps Mentor AI",
    version="0.1.0",
)


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