# RoleScope - Resume Job Role Prediction Website

Professional full-stack web app that accepts a resume and predicts the best-fit job role with confidence scores and skill insights.

## Unique Features
- Top-3 role prediction with confidence bars
- Resume skill extraction and fit analysis
- Professional drag-and-drop upload UI
- Submission history with UTC + local timezone display
- LAN mode, Docker mode, and public deployment support

## Project Structure
```
job_role _prediction/
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   |-- main.py
|   |   |-- prediction_service.py
|   |   |-- resume_parser.py
|   |   |-- role_profiles.py
|   |   `-- schemas.py
|   `-- models/
|-- frontend/
|   |-- index.html
|   `-- assets/
|       |-- css/styles.css
|       `-- js/app.js
|-- scripts/
|   |-- start.sh
|   `-- start_public_tunnel.sh
|-- tests/
|   |-- conftest.py
|   `-- test_api.py
|-- run.py
|-- requirements.txt
|-- Dockerfile
|-- docker-compose.yml
|-- Procfile
|-- render.yaml
`-- README.md
```

## Local Setup (LAN)
### 1) Create environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Run server
```bash
python run.py
```

### 4) Open on devices in same network
- This machine: `http://127.0.0.1:8000`
- Other devices on same Wi-Fi/LAN: `http://<YOUR_MACHINE_IP>:8000`

## Public Access From Any Network
If you want access from any network (mobile data, other Wi-Fi, other cities/countries), use one of these:

### Option A: Always-on (recommended)
Deploy to a cloud host (Render/Railway/AWS/GCP/Azure). This is required for "any time" availability.

#### Render (quickest)
1. Push this project to GitHub.
2. In Render, create a new Web Service from that repo.
3. Render auto-detects `render.yaml`.
4. App starts with:
   `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Use the generated public HTTPS URL from any device/network.

### Option B: Instant public URL (while your machine stays on)
```bash
bash scripts/start_public_tunnel.sh
```
Requirements:
- `cloudflared` installed
- your laptop/server must remain running and connected

## Docker Deployment
```bash
docker compose up --build -d
```
Open:
- `http://127.0.0.1:8000`
- `http://<SERVER_IP>:8000`

## Timezone Behavior
- Backend records processing timestamps in UTC.
- Frontend shows timestamps in each user's local timezone.
- Works correctly for users in different time zones.

## API Endpoints
- `GET /api/health`
- `POST /api/predict` (multipart form field: `resume`)

## Run Tests
```bash
pytest -q
```

## Important Notes
- Browsers cannot auto-read Desktop files for security reasons; users must select the file manually from Desktop.
- A local machine cannot be reachable "any time" if it is turned off or disconnected. For true 24/7 global access, deploy to cloud.
