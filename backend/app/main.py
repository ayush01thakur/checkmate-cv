from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import resume


app = FastAPI(
    title = "Resume Analyser",
    description= "Upload a resume + Job Description, get AI Feedback on Improving it.",
    version = "1.0.0"
)


# cors- allow my frontend (different ports) to call this api
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers=["*"],
)



app.include_router(resume.router, prefix="/api/v1", tags=['Resume'])


@app.get("/health")
def health_check():
    return {"status":"ok", "env":"running"}


@app.get("/")
def home():
    return {"Hellow":"home"}