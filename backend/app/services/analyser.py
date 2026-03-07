# backend/app/services/analyzer.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings
from app.schemas.resume import ResumeAnalysis

# Initialize once at module level — not inside the function
llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.3
)

prompt = ChatPromptTemplate.from_template("""
You are a senior technical recruiter and resume reviewer with experience evaluating early-career and fresher candidates.

Your task is to critically analyze the candidate's resume against the provided job description.

Be strict and objective. Assume recruiters spend only 20–30 seconds scanning a resume, so focus on signals that quickly indicate whether the candidate is strong, average, or inexperienced.

Evaluate the resume using the following criteria:

1. Skill and Qualificaitons Alignment
Check whether the qualifications and skills listed in the resume match the technologies, tools, and competencies mentioned in the job description.
Penalize generic or unrelated skill or qualificaiton lists.

2. Evidence of Skills
Verify whether listed skills are supported by projects, experience, or achievements.
If many skills appear without proof or usage, consider it a red flag.

3. Project Depth
Evaluate the quality of projects.
Strong projects describe:
- the problem solved
- tools/technologies used
- dataset or system involved
- measurable results or outcomes

Weak projects are vague, copied, or only mention a project title without explanation.

4. Impact and Metrics
Check whether the candidate quantified results (accuracy, performance improvements, time saved, revenue impact, etc.).
Lack of metrics reduces credibility.

5. Relevance of Work
Evaluate whether projects, coursework, or experience are relevant to the job role.
Penalize unrelated or filler content.

6. Professional Resume Structure
Check if the resume appears professional:
- clear sections (skills, projects, education)
- concise bullet points
- no large paragraphs
- logical structure

7. Red Flags Common in Fresher Resumes
Look for warning signals such as:
- buzzword-heavy skill lists
- vague project descriptions
- irrelevant certifications
- no portfolio/GitHub for technical roles
- grammar issues
- overly long resume
- too many unrelated skills

8. Overall Fit
Estimate how likely this candidate would pass an initial recruiter screening for this job.

Return a strict evaluation.

Respond ONLY with a raw JSON object. Do NOT include markdown, explanations, or code blocks.

JSON format:
{{
  "fit_score": <integer between 0 and 100>,
  "summary": "<2-3 sentence overall assessment of the candidate>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
  "cover_letter": "<professional 2-3 paragraph cover letter tailored to the job>"
}}

Scoring guidelines:
90-100 = Excellent match, strong evidence of skills
75-89 = Good match but with minor gaps
60-74 = Moderate match, needs improvements
40-59 = Weak alignment
0-39 = Poor fit

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
""")

parser = JsonOutputParser()

chain = prompt | llm | parser


def analyze_resume(resume_text: str, job_description: str) -> ResumeAnalysis:
    """
    Takes resume text + job description.
    Returns structured ResumeAnalysis.
    Raises ValueError if LLM fails or returns bad data.
    """

    # Truncate resume if too long — free tier has token limits
    # 3000 words is roughly 4000 tokens, safe for flash-lite
    words = resume_text.split()
    if len(words) > 3500:
        resume_text = " ".join(words[:3500])

    try:
        result = chain.invoke({
            "resume_text": resume_text,
            "job_description": job_description
        })

        # Pydantic validates the structure — missing fields = clear error
        return ResumeAnalysis(**result)

    except KeyError as e:
        raise ValueError(f"LLM response missing field: {str(e)}")
    except Exception as e:
        raise ValueError(f"Analysis failed: {str(e)}")