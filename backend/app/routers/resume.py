from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.parser import extract_text_from_pdf
from app.services.analyser import analyze_resume
from app.schemas.resume import ResumeAnalysis

router = APIRouter()

@router.post("/analyze", response_model=ResumeAnalysis)
async def analyze_resume_route(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Validate file type
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    # Validate job description isn't empty
    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    # Read file bytes
    file_bytes = await resume.read()

    # Extract text from PDF
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Analyze with LLM
    try:
        analysis = analyze_resume(resume_text, job_description)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return analysis
