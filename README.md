# AI Student Learning Tool

A self-hosted, privacy-first AI study companion that transforms your learning materials into interactive quizzes and flashcards.

# 🚀 Background

AI Student Learning Tool is an open-source, locally powered study assistant designed for students, teachers, and lifelong learners.
By combining FastAPI, React, and Ollama’s on-device AI, it enables users to upload documents (PDF, TXT, DOCX) and instantly transform them into structured lessons, summaries, and AI-generated quizzes — all processed locally without relying on external APIs.

This tool empowers learners to study smarter with full control over their data, customizable AI prompts, and the ability to host and run everything on their own machine.

## ⚙️ Key Features

- 🧩 Document Sectionization — Automatically breaks long texts into logical modules and topics.
- 🗒️ AI Summarization — Generates concise summaries and flashcards for quick reviews.
- 🎯 Quiz Generation — Creates multiple-choice questions based on the uploaded content.
- 💾 Local-First Storage — Uses SQLite for self-hosted setups or Supabase for cloud-based sync.
- 🔒 Self-Hosting Ready — Full privacy and control; no data leaves your system.
- 🤖 Powered by Ollama — Integrates local AI models like Llama 3, Phi 3, or Mistral 7B for offline intelligence.

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

## How to Contribute

1. Fork the repository

- Create your own copy of the project on GitHub

2. Find an issue or create one

- Check the repository's issues tab for tasks to work on

3. Create a pull request

- Submit your changes for review

4. Get it merged
   Once approved, your contribution will be part of the project!

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
