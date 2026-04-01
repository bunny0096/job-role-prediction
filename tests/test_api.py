from io import BytesIO

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_resume_txt() -> None:
    resume_text = (
        "Education\n"
        "B.Tech in Computer Science, ABC University, 2022\n\n"
        "Experience\n"
        "Machine Learning Intern, 2023 - Present\n"
        "Built Python and FastAPI services for model deployment and improved latency by 25%.\n\n"
        "Skills\n"
        "Python, machine learning, pandas, numpy, SQL, Docker, FastAPI, cloud, MLOps\n\n"
        "Projects\n"
        "Created a prediction platform using Docker and FastAPI for experimentation workflows.\n\n"
        "Certifications\n"
        "AWS Certified Cloud Practitioner, 2024\n"
    )
    files = {"resume": ("resume.txt", BytesIO(resume_text.encode("utf-8")), "text/plain")}

    response = client.post("/api/predict", files=files)
    assert response.status_code == 200

    payload = response.json()
    assert payload["predicted_role"]
    assert len(payload["top_matches"]) >= 1
    assert payload["confidence"] >= 0
    assert payload["resume_score"]["score"] >= 0
    assert payload["resume_score"]["max_score"] == 100
    assert len(payload["resume_score"]["section_breakdown"]) == 5
    assert {item["name"] for item in payload["resume_score"]["section_breakdown"]} == {
        "Education",
        "Experience",
        "Skills",
        "Projects",
        "Certifications",
    }
    assert payload["skill_comparison"]["role"] == payload["predicted_role"]
    assert isinstance(payload["improvement_suggestions"], list)
    assert len(payload["interview_questions"]) >= 3


def test_unsupported_file_type() -> None:
    files = {"resume": ("resume.csv", BytesIO(b"name,skills"), "text/csv")}

    response = client.post("/api/predict", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
