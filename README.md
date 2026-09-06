# Vidya — AI-Powered Inclusive Education Platform

An adaptive learning platform that makes course content (PDFs, videos, images) accessible
for students with visual, hearing, cognitive, or motor challenges — AI-generated image
descriptions, MathML + spoken math, transcripts, simplified explanations, Hindi translation,
and an AI tutor chat.

## Stack

- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + SQLite (SQLAlchemy)
- **AI:** Google Gemini (free tier) — `gemini-2.5-flash`, text + multimodal (image/PDF)

## Project structure

```
vidyanew/
├── src/                    # React frontend
│   ├── services/
│   │   ├── authService.ts           # calls /api/auth/teacher-login, /api/me
│   │   ├── aiService.ts             # calls /api/ai/chat, /simplify, /translate, /analyze-quiz
│   │   └── contentProcessingService.ts  # calls /api/process-resource (real file upload)
│   └── ...
└── backend/                # FastAPI backend
    ├── main.py              # app entrypoint
    ├── database.py          # SQLite/SQLAlchemy setup
    ├── models.py             # Teacher, Session tables
    ├── schemas.py            # Pydantic request/response shapes
    ├── ai_provider.py        # Gemini wrapper (text + multimodal)
    ├── seed.py                # creates the demo teacher account
    └── routers/
        ├── auth.py            # /api/auth/teacher-login, /api/me
        ├── ai.py               # /api/ai/*
        └── process.py          # /api/process-resource
```

## Setup — do this once

### 1. Get a free Gemini API key
Go to https://aistudio.google.com/apikey → sign in with Google → create a key.
This is free (no credit card) with generous daily limits — plenty for a demo/hackathon.

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# open .env and paste your key: GEMINI_API_KEY=your_key_here

python seed.py          # creates the demo teacher account (only needed once)
uvicorn main:app --reload --port 8000
```
Backend now runs at http://localhost:8000. Check http://localhost:8000/api/health → `{"status":"ok"}`.

### 3. Frontend setup (separate terminal)
```bash
npm install
npm run dev
```
Frontend runs at http://localhost:3000 and proxies all `/api/*` calls to the backend
(see `vite.config.ts`).

## Demo login

**Teacher:** Teacher ID `T-1082`, password `demo123` (seeded by `seed.py`)
**Student:** no login needed — click "Continue as Student" (uses local demo data, unchanged)

## What's real vs. what's still demo data

| Feature | Status |
|---|---|
| Teacher login | Real (SQLite-backed, via FastAPI) |
| AI Tutor chat | Real (Gemini) — falls back to canned answers if backend/key is down |
| Simplify text / Translate to Hindi | Real (Gemini) — same fallback behavior |
| Quiz performance analysis | Real (Gemini) — same fallback behavior |
| **File upload → accessibility content generation** | Real (Gemini multimodal) for PDF/image files — falls back to demo content for video/audio (not wired to a transcription model yet) or if no file is selected |
| Courses, quizzes, student progress, notes, notifications | Still local demo data (`seedData.ts` + localStorage) — not backed by the database yet |

## Important note on the AI fallback pattern

Every AI-backed service call tries the real backend first, and **silently falls back**
to a canned demo response if the backend is unreachable or the API key isn't set.
This is intentional — it means the demo never visibly breaks even if Gemini's free-tier
rate limit is hit mid-demo. Check your browser console for `[aiService]` or
`[contentProcessingService]` warnings if you want to confirm whether a response was
real or fallback.
