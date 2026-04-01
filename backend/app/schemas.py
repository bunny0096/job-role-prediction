"""Pydantic response schemas for API docs and validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RoleMatch(BaseModel):
    role: str
    confidence: float = Field(ge=0, le=100)
    description: str
    matched_skills: list[str]
    missing_skills: list[str]

class ResumeScoreSection(BaseModel):
    name: str
    detected: bool
    score: int = Field(ge=0, le=25)
    max_score: int = Field(ge=1, le=25)
    feedback: str


class ResumeScore(BaseModel):
    score: int = Field(ge=0, le=100)
    max_score: int = Field(ge=1, le=100)
    summary: str
    industry_fit_score: int = Field(ge=0, le=20)
    industry_fit_max_score: int = Field(ge=1, le=20)
    section_breakdown: list[ResumeScoreSection]


class SkillComparison(BaseModel):
    role: str
    alignment_percentage: int = Field(ge=0, le=100)
    required_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]


class PredictionResponse(BaseModel):
    predicted_role: str
    confidence: float = Field(ge=0, le=100)
    top_matches: list[RoleMatch]
    resume_skills: list[str]
    resume_score: ResumeScore
    skill_comparison: SkillComparison
    improvement_suggestions: list[str]
    interview_questions: list[str]
    processed_at_utc: str


class HealthResponse(BaseModel):
    status: str
    service: str
