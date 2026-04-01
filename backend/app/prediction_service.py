"""Core job-role prediction service."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .resume_analysis import analyze_resume
from .role_profiles import ALL_SKILLS, ROLE_PROFILES

TOKEN_PATTERN = re.compile(r"[^a-z0-9+.#]+")


@dataclass
class Prediction:
    role: str
    confidence: float
    description: str
    matched_skills: list[str]
    missing_skills: list[str]


class RolePredictor:
    def __init__(self) -> None:
        self.roles = list(ROLE_PROFILES.keys())
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        role_corpus = [ROLE_PROFILES[role]["profile_text"] for role in self.roles]
        self.role_vectors = self.vectorizer.fit_transform(role_corpus)

    def predict(self, resume_text: str, top_k: int = 3) -> tuple[list[Prediction], list[str]]:
        cleaned_resume = _normalize_text(resume_text)
        if len(cleaned_resume) < 30:
            raise ValueError("Resume content is too short. Please upload a detailed resume.")

        resume_vector = self.vectorizer.transform([cleaned_resume])
        raw_scores = cosine_similarity(resume_vector, self.role_vectors).flatten()

        adjusted_scores = _normalize_scores(raw_scores.tolist())
        ordered_indices = sorted(
            range(len(self.roles)), key=lambda idx: adjusted_scores[idx], reverse=True
        )

        top_indices = ordered_indices[:top_k]
        extracted_skills = _extract_skills(cleaned_resume)
        predictions = [
            self._build_prediction(self.roles[idx], adjusted_scores[idx], extracted_skills)
            for idx in top_indices
        ]
        return predictions, extracted_skills

    def _build_prediction(
        self, role: str, confidence: float, extracted_skills: list[str]
    ) -> Prediction:
        role_config = ROLE_PROFILES[role]
        role_skill_pairs = [
            (skill, _normalize_skill(skill)) for skill in role_config["skills"]
        ]

        matched = [skill for skill, normalized in role_skill_pairs if normalized in extracted_skills]
        missing = [skill for skill, normalized in role_skill_pairs if normalized not in extracted_skills]

        return Prediction(
            role=role,
            confidence=round(confidence * 100, 2),
            description=role_config["description"],
            matched_skills=matched[:8],
            missing_skills=missing[:8],
        )


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = TOKEN_PATTERN.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_skill(skill: str) -> str:
    return _normalize_text(skill)


def _normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []

    positive = [max(score, 0.0) for score in scores]
    total = sum(positive)

    if total <= 1e-9:
        base = 1.0 / len(scores)
        return [base for _ in scores]

    sharpened = [math.pow(score / total, 0.7) for score in positive]
    norm = sum(sharpened)
    return [score / norm for score in sharpened]


def _extract_skills(cleaned_text: str) -> list[str]:
    found: list[str] = []
    for skill in ALL_SKILLS:
        normalized_skill = _normalize_skill(skill)
        if not normalized_skill or normalized_skill in found:
            continue
        pattern = rf"(?<!\w){re.escape(normalized_skill)}(?!\w)"
        if re.search(pattern, cleaned_text):
            found.append(normalized_skill)

    return sorted(found)


def to_response_payload(
    predictions: list[Prediction], extracted_skills: list[str], resume_text: str
) -> dict[str, Any]:
    top = predictions[0]
    payload = {
        "predicted_role": top.role,
        "confidence": top.confidence,
        "top_matches": [prediction.__dict__ for prediction in predictions],
        "resume_skills": extracted_skills[:25],
    }
    payload.update(analyze_resume(resume_text, top.role, extracted_skills))
    return payload
