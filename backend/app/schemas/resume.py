from pydantic import BaseModel

class AnalyseRequest(BaseModel):
    job_description: str

class ResumeAnalysis(BaseModel):
    fit_score:int
    summary:str
    strengths: list[str]
    improvements: list[str]
    cover_letter: str