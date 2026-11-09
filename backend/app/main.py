from fastapi import FastAPI

app = FastAPI(title="pasz-lab4")


@app.get("/api/health")
def health():
    return {"status": "ok"}
