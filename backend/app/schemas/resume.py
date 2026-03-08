from pydantic import BaseModel

class AnalyseRequest(BaseModel):
    job_description: str

# class ResumeAnalysis(BaseModel):
#     fit_score:int
#     summary:str
#     strengths: list[str]
#     improvements: list[str]
#     cover_letter: str
#     resume_text: str


class LLMAnalysis(BaseModel):
    fit_score: int
    summary: str
    strengths: list[str]
    improvements: list[str]
    cover_letter: str

class ResumeAnalysis(LLMAnalysis):
    resume_text: str 