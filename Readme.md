# CheckmateCV 🎯

AI-powered resume analyzer and enhancer. Upload your resume, paste a job description, get a fit score, tailored feedback, and a fully optimized resume for the specified JD and it updates the resume with your inputs in loop.

**Live Demo → [CheckMate-CV](https://ai-resume-analyzer-frontend-erc7.onrender.com/)**

---

## What it does

1. **Analyze** — Upload PDF resume + job description → get fit score, strengths, improvements, cover letter
2. **Enhance** — Fill a dynamic AI-generated form with missing info (projects, experience, skills)
3. **Download** — Get a rebuilt ATS-optimized resume as PDF + cold outreach message for LinkedIn/email

---

## Tech Stack

`FastAPI` `LangChain` `Google Gemini` `pypdf` `Docker` `Nginx` `Render`

---

## Run Locally

### With Docker
```bash
git clone https://github.com/ayush01thakur/checkmatecv.git
cd checkmatecv

cp backend/.env.example backend/.env
# Add your GEMINI_API_KEY to backend/.env

docker compose up --build
```
- Frontend → `http://localhost`
- API docs → `http://localhost:8000/docs`

### Without Docker
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
cp .env.example .env         # Add your GEMINI_API_KEY

uvicorn app.main:app --reload --port 8000
```
Then open `frontend/index.html` in your browser.

---

## Environment Variables

```bash
# backend/.env
GEMINI_API_KEY=        # https://aistudio.google.com/apikey
GEMINI_MODEL=gemini-2.5-flash-lite
APP_ENV=development
```

---

## API Routes

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/stats` | Analyzed + updated counts |
| POST | `/api/v1/analyze` | Analyze resume vs JD |
| POST | `/api/v1/generate-form` | Generate dynamic form |
| POST | `/api/v1/enhance` | Build enhanced resume |

---

## Known Limitations

- Scanned/image PDFs cannot be parsed — use text-based PDFs
- Free tier Gemini has rate limits — wait and retry if hit
- Stats counter resets on server restart (in-memory, no DB yet)
- Render free tier has ~30s cold start after inactivity

---

## Built by

**Ayush Kumar Thakur** — [thakur8ayush@gmail.com](mailto:thakur8ayush@gmail.com) · [LinkedIn](https://www.linkedin.com/in/ayush-kumar-thakur-ba6402252/)