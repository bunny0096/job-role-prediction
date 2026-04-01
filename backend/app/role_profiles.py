"""Role profiles used for semantic resume-role matching."""

ROLE_PROFILES = {
    "Data Scientist": {
        "description": "Builds predictive models, analyzes datasets, and communicates business insights.",
        "skills": [
            "python",
            "machine learning",
            "statistics",
            "pandas",
            "numpy",
            "feature engineering",
            "model evaluation",
            "data visualization",
            "sql",
            "experimentation",
        ],
        "profile_text": (
            "data scientist machine learning python statistics hypothesis testing "
            "feature engineering predictive modeling model evaluation pandas numpy "
            "data storytelling sql analytics business insight"
        ),
    },
    "Machine Learning Engineer": {
        "description": "Designs and deploys scalable ML systems for production use.",
        "skills": [
            "python",
            "mlops",
            "model deployment",
            "docker",
            "fastapi",
            "pytorch",
            "tensorflow",
            "ci/cd",
            "api development",
            "cloud",
        ],
        "profile_text": (
            "machine learning engineer mlops model deployment production inference "
            "python fastapi docker kubernetes ci cd cloud tensorflow pytorch monitoring"
        ),
    },
    "Backend Developer": {
        "description": "Builds APIs, services, and databases that power applications.",
        "skills": [
            "python",
            "java",
            "node.js",
            "rest api",
            "microservices",
            "postgresql",
            "redis",
            "authentication",
            "system design",
            "testing",
        ],
        "profile_text": (
            "backend developer api microservices rest graphql authentication authorization "
            "database postgresql mysql redis caching scalability python java node system design"
        ),
    },
    "Frontend Developer": {
        "description": "Creates responsive, interactive web user interfaces.",
        "skills": [
            "javascript",
            "typescript",
            "react",
            "css",
            "html",
            "responsive design",
            "accessibility",
            "redux",
            "vite",
            "ui testing",
        ],
        "profile_text": (
            "frontend developer react javascript typescript html css responsive web "
            "state management redux accessibility ui performance testing"
        ),
    },
    "Full Stack Developer": {
        "description": "Works across frontend and backend to deliver complete products.",
        "skills": [
            "javascript",
            "react",
            "node.js",
            "python",
            "api integration",
            "database",
            "full stack",
            "deployment",
            "git",
            "testing",
        ],
        "profile_text": (
            "full stack developer frontend backend react node python api integration "
            "database deployment testing git agile product development"
        ),
    },
    "DevOps Engineer": {
        "description": "Automates infrastructure, release pipelines, and observability.",
        "skills": [
            "docker",
            "kubernetes",
            "terraform",
            "aws",
            "azure",
            "ci/cd",
            "linux",
            "monitoring",
            "prometheus",
            "incident response",
        ],
        "profile_text": (
            "devops engineer infrastructure automation kubernetes docker terraform cloud aws "
            "azure ci cd linux monitoring prometheus grafana reliability"
        ),
    },
    "Cybersecurity Analyst": {
        "description": "Protects systems through monitoring, auditing, and incident response.",
        "skills": [
            "security monitoring",
            "siem",
            "network security",
            "vulnerability assessment",
            "incident response",
            "python",
            "compliance",
            "risk management",
            "soc",
            "threat intelligence",
        ],
        "profile_text": (
            "cybersecurity analyst security monitoring siem incident response threat detection "
            "vulnerability assessment risk compliance soc network security"
        ),
    },
    "Business Analyst": {
        "description": "Translates business needs into data-backed product requirements.",
        "skills": [
            "requirements gathering",
            "stakeholder management",
            "sql",
            "excel",
            "data analysis",
            "documentation",
            "process mapping",
            "kpi",
            "dashboard",
            "communication",
        ],
        "profile_text": (
            "business analyst requirements gathering stakeholder communication process mapping "
            "sql excel dashboard kpi reporting user stories documentation"
        ),
    },
    "Product Manager": {
        "description": "Defines product strategy, roadmap, and cross-functional execution.",
        "skills": [
            "product strategy",
            "roadmap",
            "market research",
            "user research",
            "agile",
            "prioritization",
            "analytics",
            "a/b testing",
            "stakeholder communication",
            "go-to-market",
        ],
        "profile_text": (
            "product manager strategy roadmap prioritization user research market analysis "
            "agile sprint planning cross functional leadership experimentation"
        ),
    },
    "Cloud Engineer": {
        "description": "Designs, secures, and optimizes cloud architecture and operations.",
        "skills": [
            "aws",
            "azure",
            "gcp",
            "cloud architecture",
            "networking",
            "iam",
            "docker",
            "kubernetes",
            "cost optimization",
            "automation",
        ],
        "profile_text": (
            "cloud engineer aws azure gcp cloud architecture iam networking automation "
            "kubernetes docker reliability cost optimization"
        ),
    },
}

ALL_SKILLS = sorted(
    {skill.lower() for role in ROLE_PROFILES.values() for skill in role["skills"]}
)
