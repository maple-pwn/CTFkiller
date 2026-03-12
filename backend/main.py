from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.sessions import router as sessions_router
from backend.database.connection import init_db

app = FastAPI(title="LLM Agent Workspace System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "healthy"}
