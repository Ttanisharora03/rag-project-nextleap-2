import logging
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
from pathlib import Path

from src.api.routes import router

# Configure basic logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Mutual Fund FAQ Assistant",
    description="RAG Chatbot API for ICICI Prudential mutual fund queries",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api")

# Mount frontend static files
project_root = Path(__file__).resolve().parent.parent.parent
frontend_dir = project_root / "frontend"

if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    async def serve_index():
        return {"message": "API is running. Frontend directory not found."}
