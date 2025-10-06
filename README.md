# Personal Study Companion

Lightweight full-stack study helper: a React + Vite frontend with a FastAPI backend that parses and stores study documents (PDF, DOCX, TXT) into a local SQLite database. The project includes Docker configuration to run the app using docker-compose during development.

## Overview

- Backend: FastAPI (Python) — located in `backend/main.py` (document parsing, basic auth, SQLite storage)
- Frontend: React + Vite — located in `web-app/` (development server via Vite, production build served with Nginx in Dockerfile)
- Database: SQLite file at `backend/study_tool.db` (created/used by the backend)
- AI / LLM: Ollama can be integrated locally; the backend assumes an external LLM service for advanced features.

## Repo layout (high level)

- `backend/` — FastAPI app and local SQLite DB
- `web-app/` — React + Vite frontend
- `docker-compose.yml` — development compose file (frontend + backend)
- `Dockerfile`, `Dockerfile.dev` in each service for container builds

## Quick start — Local (recommended for development)

Windows (PowerShell) — backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# If a requirements.txt exists: pip install -r requirements.txt
# Otherwise install minimal deps:
pip install fastapi uvicorn PyPDF2 python-docx python-multipart
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (PowerShell)

```powershell
cd web-app
# Use npm or yarn depending on your preference
npm install
npm run dev
# or: yarn install && yarn dev
```

Backend health & docs should be available at http://localhost:8000 and OpenAPI at http://localhost:8000/docs (when running with uvicorn as above).

## Quick start — Docker (development)

The repository includes a `docker-compose.yml` to bring up both frontend and backend in development mode. From the project root run:

```powershell
docker-compose up --build
```

Useful scripts (from `package.json`):

```powershell
npm run docker:dev   # runs `docker-compose up --build`
npm run docker:down  # runs `docker-compose down`
npm run docker:logs  # runs `docker-compose logs -f`
```

Services & ports (as configured in `docker-compose.yml`):

- `frontend` (container name `study-web`) — Vite dev server mapped to host port 5173 (development). In production Dockerfile it is built and served by Nginx on port 80.
- `backend` (container name `study-backend`) — mapped to host port 5000 in compose

Note: when using the local uvicorn run (not Docker), the backend in this repo listens on port 8000 by default (see `backend/main.py`). The compose file maps `backend:5000:5000` — verify which server you want inside the container.

## Database

The app uses a local SQLite file at `backend/study_tool.db`. The `backend/main.py` file contains an `init_db()` routine that will create necessary tables automatically when the app starts.

## AI/LLM integration

This project references Ollama for local LLM usage. Make sure your Ollama daemon or chosen LLM endpoint is running and that the backend is configured to connect to it if you plan to use AI features.

## Notes & TODOs

- The backend implementation is a Python FastAPI app (see `backend/main.py`). However, there are Dockerfiles in `backend/` that currently use Node images — if you plan to run the Python backend inside Docker, update the backend Dockerfile to use a Python base image and install the Python dependencies.
- Add a `requirements.txt` (or a proper Dockerfile for Python) to make the backend Docker build reproducible.
- Add tests and CI for both frontend and backend.

## License

MIT
