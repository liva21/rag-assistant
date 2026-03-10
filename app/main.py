from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Omi RAG Assistant")

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Omi API is online"}
