"""FastAPI app for resume-based job role prediction."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .prediction_service import RolePredictor, to_response_payload
from .resume_parser import ResumeParsingError, extract_text
from .schemas import HealthResponse, PredictionResponse

predictor = RolePredictor()

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/", include_in_schema=False)
def serve_index() -> FileResponse:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found")
    return FileResponse(index_path)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name)


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_job_role(resume: UploadFile = File(...)) -> dict:
    file_name = resume.filename or "uploaded_resume"
    suffix = Path(file_name).suffix.lower()

    if suffix not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(settings.allowed_extensions)}",
        )

    file_bytes = await resume.read()
    max_bytes = settings.max_resume_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum allowed size: {settings.max_resume_size_mb} MB",
        )

    try:
        resume_text = extract_text(file_name=file_name, file_bytes=file_bytes)
    except ResumeParsingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        predictions, extracted_skills = predictor.predict(resume_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = to_response_payload(predictions, extracted_skills, resume_text)
    payload["processed_at_utc"] = datetime.now(timezone.utc).isoformat()
    return payload
