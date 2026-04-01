"""Resume scoring and post-prediction analysis helpers."""

from __future__ import annotations

import re

from .role_profiles import ROLE_PROFILES

TOKEN_PATTERN = re.compile(r"[^a-z0-9+.#]+")
METRIC_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%?\b")
YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")
DATE_RANGE_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\s*(?:-|to|–|\s+)\s*(?:present|current|now|(?:19|20)\d{2})\b"
)
ACTION_VERB_PATTERN = re.compile(
    r"\b(?:built|created|delivered|deployed|designed|developed|implemented|improved|led|managed|optimized)\b"
)

SECTION_CONFIG = {
    "education": {
        "title": "Education",
        "weight": 15,
        "aliases": [
            "education",
            "academic background",
            "academic qualifications",
            "qualifications",
        ],
        "fallback_patterns": [
            re.compile(
                r"\b(?:bachelor|master|b\.?tech|m\.?tech|b\.?e|m\.?e|mba|phd|doctorate)\b"
            ),
            re.compile(r"\b(?:university|college|institute|school)\b"),
        ],
        "suggestion": "Add an Education section with your degree, institution, and graduation year.",
    },
    "experience": {
        "title": "Experience",
        "weight": 20,
        "aliases": [
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "internship experience",
        ],
        "fallback_patterns": [
            re.compile(r"\b(?:experience|internship|employment|worked|engineer|analyst|developer)\b"),
            DATE_RANGE_PATTERN,
        ],
        "suggestion": "Add an Experience section with role names, dates, and measurable impact.",
    },
    "skills": {
        "title": "Skills",
        "weight": 20,
        "aliases": [
            "skills",
            "technical skills",
            "core skills",
            "competencies",
            "key skills",
        ],
        "fallback_patterns": [],
        "suggestion": "Add a Skills section that lists the tools, languages, and platforms you actually used.",
    },
    "projects": {
        "title": "Projects",
        "weight": 15,
        "aliases": [
            "projects",
            "project experience",
            "academic projects",
            "personal projects",
        ],
        "fallback_patterns": [
            re.compile(r"\b(?:project|prototype|capstone|github|portfolio)\b"),
        ],
        "suggestion": "Add a Projects section with role-relevant work, technologies used, and outcomes.",
    },
    "certifications": {
        "title": "Certifications",
        "weight": 10,
        "aliases": [
            "certifications",
            "certification",
            "licenses",
            "certificates",
            "courses",
        ],
        "fallback_patterns": [
            re.compile(r"\b(?:certification|certified|certificate|license|credential)\b"),
            re.compile(r"\b(?:aws|azure|google|oracle|cisco|coursera|udemy|scrum)\b"),
        ],
        "suggestion": "Add Certifications if you have relevant credentials, or remove the gap by building evidence in projects.",
    },
}


def analyze_resume(
    resume_text: str, predicted_role: str, extracted_skills: list[str]
) -> dict[str, object]:
    normalized_resume = _normalize_text(resume_text)
    parsed_sections = _extract_sections(resume_text)

    role_skill_pairs = [
        (skill, _normalize_text(skill)) for skill in ROLE_PROFILES[predicted_role]["skills"]
    ]
    matched_skills = [label for label, normalized in role_skill_pairs if normalized in extracted_skills]
    missing_skills = [
        label for label, normalized in role_skill_pairs if normalized not in extracted_skills
    ]
    alignment_percentage = round((len(matched_skills) / max(1, len(role_skill_pairs))) * 100)
    industry_fit_score = round((alignment_percentage / 100) * 20)

    section_breakdown: list[dict[str, object]] = []
    section_points = 0

    for section_key, config in SECTION_CONFIG.items():
        section_input = _resolve_section_text(
            section_key=section_key,
            parsed_sections=parsed_sections,
            normalized_resume=normalized_resume,
            resume_text=resume_text,
            extracted_skills=extracted_skills,
        )
        analysis = _analyze_section(section_key, section_input, extracted_skills)
        section_breakdown.append(
            {
                "name": config["title"],
                "detected": analysis["detected"],
                "score": analysis["score"],
                "max_score": config["weight"],
                "feedback": analysis["feedback"],
            }
        )
        section_points += analysis["score"]

    detected_sections = sum(1 for item in section_breakdown if item["detected"])
    resume_score = min(100, section_points + industry_fit_score)
    suggestions = _build_suggestions(
        predicted_role=predicted_role,
        section_breakdown=section_breakdown,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        extracted_skills=extracted_skills,
        parsed_sections=parsed_sections,
    )
    summary = (
        f"{detected_sections}/5 key sections detected with {alignment_percentage}% alignment "
        f"to {predicted_role} industry skills."
    )

    return {
        "resume_score": {
            "score": resume_score,
            "max_score": 100,
            "summary": summary,
            "industry_fit_score": industry_fit_score,
            "industry_fit_max_score": 20,
            "section_breakdown": section_breakdown,
        },
        "skill_comparison": {
            "role": predicted_role,
            "alignment_percentage": alignment_percentage,
            "required_skills": [label for label, _ in role_skill_pairs],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        },
        "improvement_suggestions": suggestions,
        "interview_questions": _generate_interview_questions(
            predicted_role=predicted_role,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
        ),
    }


def _extract_sections(resume_text: str) -> dict[str, str]:
    sections = {key: [] for key in SECTION_CONFIG}
    current_section: str | None = None

    for raw_line in resume_text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue

        section_name = _match_section_heading(line)
        if section_name:
            current_section = section_name
            continue

        if current_section:
            sections[current_section].append(line)

    return {key: " ".join(values).strip() for key, values in sections.items() if values}


def _match_section_heading(line: str) -> str | None:
    normalized_line = _normalize_text(line).rstrip(":")
    for section_key, config in SECTION_CONFIG.items():
        aliases = [_normalize_text(alias) for alias in config["aliases"]]
        if normalized_line in aliases:
            return section_key
    return None


def _resolve_section_text(
    section_key: str,
    parsed_sections: dict[str, str],
    normalized_resume: str,
    resume_text: str,
    extracted_skills: list[str],
) -> dict[str, object]:
    explicit_text = parsed_sections.get(section_key, "")
    if explicit_text:
        return {"detected": True, "text": explicit_text}

    if section_key == "skills" and extracted_skills:
        return {"detected": True, "text": " ".join(extracted_skills)}

    for pattern in SECTION_CONFIG[section_key]["fallback_patterns"]:
        if pattern.search(normalized_resume):
            return {"detected": True, "text": resume_text}

    return {"detected": False, "text": ""}


def _analyze_section(
    section_key: str, section_input: dict[str, object], extracted_skills: list[str]
) -> dict[str, object]:
    detected = bool(section_input["detected"])
    section_text = str(section_input["text"])
    weight = int(SECTION_CONFIG[section_key]["weight"])

    if not detected:
        return {
            "detected": False,
            "score": 0,
            "feedback": f"{SECTION_CONFIG[section_key]['title']} section was not detected.",
        }

    presence_score = round(weight * 0.6)
    quality_ratio, feedback = _quality_ratio_for_section(
        section_key=section_key,
        section_text=section_text,
        extracted_skills=extracted_skills,
    )
    bonus_score = round((weight - presence_score) * quality_ratio)
    return {
        "detected": True,
        "score": min(weight, presence_score + bonus_score),
        "feedback": feedback,
    }


def _quality_ratio_for_section(
    section_key: str, section_text: str, extracted_skills: list[str]
) -> tuple[float, str]:
    normalized_text = _normalize_text(section_text)

    if section_key == "education":
        degree_hit = bool(
            re.search(r"\b(?:bachelor|master|b\.?tech|m\.?tech|mba|phd|doctorate)\b", normalized_text)
        )
        institution_hit = bool(re.search(r"\b(?:university|college|institute|school)\b", normalized_text))
        year_hit = bool(YEAR_PATTERN.search(normalized_text))
        clues = sum([degree_hit, institution_hit, year_hit])
        ratio = clues / 3
        if clues == 3:
            feedback = "Education includes degree, institution, and timeline details."
        elif clues == 2:
            feedback = "Education is present, but adding institution or year details would strengthen it."
        else:
            feedback = "Education is present, but the details look light."
        return ratio, feedback

    if section_key == "experience":
        date_hit = bool(DATE_RANGE_PATTERN.search(normalized_text) or YEAR_PATTERN.search(normalized_text))
        metric_hit = bool(METRIC_PATTERN.search(normalized_text))
        action_hit = bool(ACTION_VERB_PATTERN.search(normalized_text))
        clues = sum([date_hit, metric_hit, action_hit])
        ratio = clues / 3
        if clues == 3:
            feedback = "Experience includes timeline, action-driven bullets, and measurable impact."
        elif clues == 2:
            feedback = "Experience is present, but adding stronger metrics or action verbs would help."
        else:
            feedback = "Experience is present, but it needs clearer outcomes and dates."
        return ratio, feedback

    if section_key == "skills":
        skill_count = len(extracted_skills)
        if skill_count >= 8:
            return 1.0, f"Strong skill coverage detected with {skill_count} recognizable skills."
        if skill_count >= 5:
            return 0.75, f"Good skill coverage detected with {skill_count} recognizable skills."
        if skill_count >= 3:
            return 0.5, f"Basic skill coverage detected with {skill_count} recognizable skills."
        if skill_count >= 1:
            return 0.25, f"Limited skill coverage detected with {skill_count} recognizable skill."
        return 0.0, "Skills section is present, but it does not include recognizable industry keywords."

    if section_key == "projects":
        project_hit = bool(re.search(r"\b(?:project|prototype|capstone|portfolio|github)\b", normalized_text))
        metric_hit = bool(METRIC_PATTERN.search(normalized_text))
        tech_hit = sum(1 for skill in extracted_skills if skill in normalized_text) >= 2
        clues = sum([project_hit, metric_hit, tech_hit])
        ratio = clues / 3
        if clues == 3:
            feedback = "Projects show technologies used and measurable outcomes."
        elif clues == 2:
            feedback = "Projects are present, but impact or technical depth could be clearer."
        else:
            feedback = "Projects are present, but they need more role-relevant detail."
        return ratio, feedback

    certification_hit = bool(re.search(r"\b(?:certification|certified|certificate|credential|license)\b", normalized_text))
    provider_hit = bool(re.search(r"\b(?:aws|azure|google|oracle|cisco|coursera|udemy|scrum)\b", normalized_text))
    year_hit = bool(YEAR_PATTERN.search(normalized_text))
    clues = sum([certification_hit, provider_hit, year_hit])
    ratio = clues / 3
    if clues == 3:
        feedback = "Certifications include credential, issuer, and timeline information."
    elif clues == 2:
        feedback = "Certifications are present, but issuer or year details are missing."
    else:
        feedback = "Certifications are listed, but the entries look incomplete."
    return ratio, feedback


def _build_suggestions(
    predicted_role: str,
    section_breakdown: list[dict[str, object]],
    matched_skills: list[str],
    missing_skills: list[str],
    extracted_skills: list[str],
    parsed_sections: dict[str, str],
) -> list[str]:
    suggestions: list[str] = []

    for item in section_breakdown:
        if not item["detected"]:
            section_key = _normalize_text(str(item["name"]))
            suggestions.append(SECTION_CONFIG[section_key]["suggestion"])

    if missing_skills:
        suggestions.append(
            f"Add evidence of {', '.join(missing_skills[:4])} in your projects or experience to better match {predicted_role} expectations."
        )

    experience_text = _normalize_text(parsed_sections.get("experience", ""))
    if experience_text and not METRIC_PATTERN.search(experience_text):
        suggestions.append("Quantify experience bullets with metrics such as percentages, time saved, revenue, or scale.")

    if len(extracted_skills) < 6:
        suggestions.append(
            "Expand the Skills section with the languages, tools, and platforms you used most recently."
        )

    if parsed_sections.get("projects") and not METRIC_PATTERN.search(_normalize_text(parsed_sections["projects"])):
        suggestions.append("Add measurable outcomes to projects, such as accuracy gains, latency reduction, or user growth.")

    if not suggestions:
        suggestions.append(
            f"Resume coverage is strong for {predicted_role}; focus on tailoring bullet points to the target role before applying."
        )

    return suggestions[:5]


def _generate_interview_questions(
    predicted_role: str, matched_skills: list[str], missing_skills: list[str]
) -> list[str]:
    questions = [
        f"Tell me about a {predicted_role.lower()} project you are most proud of and the result it delivered.",
    ]

    if matched_skills:
        questions.append(
            f"How have you applied {matched_skills[0]} in a real project, and what trade-offs did you make?"
        )
    if len(matched_skills) > 1:
        questions.append(
            f"What best practices do you follow when working with {matched_skills[1]} in production?"
        )
    if missing_skills:
        questions.append(
            f"If this role required {missing_skills[0]}, how would you ramp up quickly and prove you can handle it?"
        )
    if len(missing_skills) > 1:
        questions.append(
            f"Describe how you would build a project to demonstrate {missing_skills[1]} for a {predicted_role.lower()} interview."
        )

    questions.append(
        f"How do you decide which problems are most important to solve first in a {predicted_role.lower()} role?"
    )
    return questions[:5]


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = TOKEN_PATTERN.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()
