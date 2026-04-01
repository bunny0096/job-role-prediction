"""Application configuration."""

from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "RoleScope - Resume Job Role Predictor"
    max_resume_size_mb: int = 8
    allowed_extensions: tuple[str, ...] = (".pdf", ".docx", ".txt")


settings = Settings()
