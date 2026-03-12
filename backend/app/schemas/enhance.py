from pydantic import BaseModel

class FormField(BaseModel):
    id: str           # unique field id e.g. "project_1_title"
    label: str        # what user sees
    type: str         # "text", "textarea", "url", "select"
    required: bool
    section: str      # "projects", "experience", "skills" etc
    placeholder: str

class DynamicForm(BaseModel):
    fields: list[FormField]

class EnhanceRequest(BaseModel):
    resume_text: str
    job_description: str
    improvements: list[str]
    form_data: dict

class EnhanceResponse(BaseModel):
    html: str
    new_fit_score: int
    cover_letter: str
    cold_message: str