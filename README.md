# PrepWise AI

Resume analysis and interview practice: resume score, Bullet Proof Score, job matching,
mock interviews, STAR check, Story Bank, Job Tracker, voice practice and Resume Defense Mode.

## Tech
React, Vite, React Router, Axios · Django, Django REST Framework, SimpleJWT · SQLite · Google Gemini (optional)

## Run it
Backend:
    cd backend
    python3.12 -m venv ../.venv && source ../.venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    export AI_PROVIDER=gemini AI_MODEL=<model> GEMINI_API_KEY=<your key>   # optional
    python manage.py runserver

Frontend (second terminal):
    cd frontend
    npm install
    npm run dev

Open http://localhost:5173. API docs: http://127.0.0.1:8000/api/docs/

Without an AI key, the app uses rule-based scoring.

## Limits
Scores are estimates from fixed rules, not official ATS or hiring results.
Automated tests were written but have not been run.