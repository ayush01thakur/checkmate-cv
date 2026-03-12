
from fastapi import APIRouter, HTTPException
from app.schemas.enhance import EnhanceRequest, EnhanceResponse, DynamicForm
from app.services.form_generator import generate_form_fields
from app.services.resume_builder import build_enhanced_resume
from app.core.counter import increment_updated

router = APIRouter()


@router.post("/generate-form", response_model=DynamicForm)
def generate_form(improvements: list[str]):
    """
    Takes improvements list from analysis.
    Returns dynamic form fields — LLM decides what to ask.
    No file upload needed, just the improvements list.
    """
    try:
        return generate_form_fields(improvements)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_resume(request: EnhanceRequest):
    """
    Takes resume text + JD + improvements + filled form data.
    Extracts existing info, merges with new data, generates resume.
    Returns HTML resume + new score + cover letter + cold message.
    """
    # Basic validation
    if not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is empty")

    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is empty")

    if not request.form_data:
        raise HTTPException(status_code=400, detail="Form data is empty")

    try:
        result = await build_enhanced_resume(
            resume_text=request.resume_text,
            job_description=request.job_description,
            form_data=request.form_data
        )

        # Only increment after successful enhancement
        increment_updated()

        return EnhanceResponse(
            html=result["html"],
            new_fit_score=result["new_fit_score"],
            cover_letter=result["cover_letter"],
            cold_message=result["cold_message"]
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))