# backend/app/services/resume_builder.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings
import json

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.3
)

# ── Step 1: Extract existing info from resume ──────────────────
extract_prompt = ChatPromptTemplate.from_template("""
Extract the following information from this resume text.
If a field is not found, use an empty string.
Respond ONLY with raw JSON. No markdown, no code blocks.

{{
  "name": "<full name>",
  "email": "<email>",
  "phone": "<phone number>",
  "linkedin": "<linkedin url>",
  "github": "<github url>",
  "location": "<city or country>",
  "education": "<education details as a single string>",
  "existing_skills": "<all skills as comma separated string>",
  "existing_experience": "<all work experience as a single string>",
  "existing_projects": "<all projects as a single string>",
  "existing_achievements": "<all achievements as a single string>"
}}

RESUME TEXT:
{resume_text}
""")

extract_chain = extract_prompt | llm | JsonOutputParser()

# ── Step 2: Build complete resume content ──────────────────────
build_prompt = ChatPromptTemplate.from_template("""
You are a professional resume writer.

Using the existing resume info and the new information provided by the candidate,
write a complete ATS-optimized resume tailored to the job description.

Rules:
- Use existing info as the base
- Enhance and fill gaps using the new info provided
- Keep all original correct information — do not remove anything valid
- Tailor content to the job description
- Quantify results wherever possible
- Keep language professional and concise
- Works for ANY role type — tech, non-tech, creative, finance, etc.
- cover_letter must be 3-4 paragraphs, tailored to the job
- cold_message must be 3-4 lines max, suitable for LinkedIn or email outreach

Respond ONLY with raw JSON. No markdown, no code blocks.

{{
  "name": "<name>",
  "email": "<email>",
  "phone": "<phone>",
  "linkedin": "<linkedin url>",
  "github": "<github url or empty>",
  "location": "<location>",
  "summary": "<2-3 line professional summary tailored to job>",
  "skills": ["<skill1>", "<skill2>", "<skill3>"],
  "experience": [
    {{
      "company": "<company name>",
      "role": "<job title>",
      "duration": "<start - end>",
      "points": ["<achievement 1>", "<achievement 2>"]
    }}
  ],
  "projects": [
    {{
      "title": "<project title>",
      "description": "<what it does, tech used, results>",
      "link": "<url or empty string>",
      "tech": "<comma separated tech stack>"
    }}
  ],
  "education": "<education as single string>",
  "achievements": ["<achievement1>", "<achievement2>"],
  "fit_score": <integer 0-100>,
  "cover_letter": "<full cover letter 3-4 paragraphs>",
  "cold_message": "<short 3-4 line cold outreach message for LinkedIn or email>"
}}

JOB DESCRIPTION:
{job_description}

EXISTING RESUME INFO:
{existing_info}

NEW INFO FROM CANDIDATE:
{new_info}
""")

build_chain = build_prompt | llm | JsonOutputParser()


# ── HTML Resume Template ───────────────────────────────────────
def build_resume_html(data: dict) -> str:
    """Converts structured resume data into clean printable HTML."""

    # Contact line
    contact_parts = []
    if data.get("email"):    contact_parts.append(data["email"])
    if data.get("phone"):    contact_parts.append(data["phone"])
    if data.get("location"): contact_parts.append(data["location"])
    if data.get("linkedin"):
        contact_parts.append(f'<a href="{data["linkedin"]}">{data["linkedin"]}</a>')
    if data.get("github"):
        contact_parts.append(f'<a href="{data["github"]}">{data["github"]}</a>')
    contact_html = " &nbsp;|&nbsp; ".join(contact_parts)

    # Experience
    experience_html = ""
    for exp in data.get("experience", []):
        if not exp.get("company"):
            continue
        points = "".join(f"<li>{p}</li>" for p in exp.get("points", []))
        experience_html += f"""
        <div class="entry">
            <div class="entry-header">
                <span class="entry-title">{exp.get('role', '')}</span>
                <span class="entry-date">{exp.get('duration', '')}</span>
            </div>
            <div class="entry-subtitle">{exp.get('company', '')}</div>
            <ul>{points}</ul>
        </div>"""

    # Projects
    projects_html = ""
    for proj in data.get("projects", []):
        if not proj.get("title"):
            continue
        link_html = ""
        if proj.get("link"):
            link_html = f'<a href="{proj["link"]}" class="proj-link">{proj["link"]}</a>'
        projects_html += f"""
        <div class="entry">
            <div class="entry-header">
                <span class="entry-title">{proj.get('title', '')}</span>
            </div>
            <div class="entry-subtitle">{proj.get('tech', '')}</div>
            <p>{proj.get('description', '')}</p>
            {link_html}
        </div>"""

    # Achievements
    achievements_html = "".join(
        f"<li>{a}</li>" for a in data.get("achievements", []) if a
    )

    # Skills
    skills_html = " &nbsp;•&nbsp; ".join(data.get("skills", []))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Georgia', serif;
    font-size: 11pt;
    color: #1a1a1a;
    padding: 40px 56px;
    max-width: 850px;
    margin: 0 auto;
    line-height: 1.5;
  }}

  /* Name */
  h1 {{
    font-size: 24pt;
    font-weight: bold;
    text-align: center;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }}

  /* Contact */
  .contact {{
    text-align: center;
    font-size: 9.5pt;
    color: #444;
    margin-bottom: 20px;
  }}
  .contact a {{ color: #444; text-decoration: none; }}

  /* Section headers */
  h2 {{
    font-size: 10.5pt;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    border-bottom: 1.5px solid #1a1a1a;
    padding-bottom: 3px;
    margin: 18px 0 10px;
  }}

  /* Summary + skills */
  .summary-text, .skills-text {{
    font-size: 10.5pt;
    color: #333;
    line-height: 1.6;
  }}

  /* Entries (experience + projects) */
  .entry {{ margin-bottom: 12px; }}
  .entry-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }}
  .entry-title {{
    font-weight: bold;
    font-size: 11pt;
  }}
  .entry-date {{
    font-size: 9.5pt;
    color: #555;
    white-space: nowrap;
  }}
  .entry-subtitle {{
    font-style: italic;
    font-size: 9.5pt;
    color: #555;
    margin-bottom: 4px;
  }}
  ul {{
    padding-left: 18px;
    margin-top: 4px;
  }}
  li {{
    font-size: 10.5pt;
    margin-bottom: 3px;
    color: #222;
  }}
  p {{
    font-size: 10.5pt;
    color: #333;
    margin-top: 3px;
  }}
  .proj-link {{
    font-size: 9.5pt;
    color: #444;
    display: block;
    margin-top: 3px;
  }}

  /* Print optimization */
  @media print {{
    body {{ padding: 24px 40px; }}
    a {{ color: #1a1a1a; }}
  }}
</style>
</head>
<body>

  <h1>{data.get('name', 'Your Name')}</h1>
  <div class="contact">{contact_html}</div>

  {"<h2>Summary</h2><p class='summary-text'>" + data['summary'] + "</p>" if data.get('summary') else ""}

  {"<h2>Skills</h2><p class='skills-text'>" + skills_html + "</p>" if skills_html else ""}

  {"<h2>Experience</h2>" + experience_html if experience_html else ""}

  {"<h2>Projects</h2>" + projects_html if projects_html else ""}

  {"<h2>Education</h2><p>" + data.get('education','') + "</p>" if data.get('education') else ""}

  {"<h2>Achievements</h2><ul>" + achievements_html + "</ul>" if achievements_html else ""}

</body>
</html>"""


# ── Main function ──────────────────────────────────────────────
async def build_enhanced_resume(
    resume_text: str,
    job_description: str,
    form_data: dict
) -> dict:
    """
    1. Extract existing info from resume text
    2. Merge with new form data
    3. Generate complete resume via LLM
    4. Build HTML
    5. Return full result dict
    """

    # Step 1 — extract existing info
    try:
        existing_info = extract_chain.invoke({"resume_text": resume_text})
    except Exception as e:
        raise ValueError(f"Failed to extract resume info: {str(e)}")

    # Step 2 — build new resume via LLM
    try:
        resume_data = build_chain.invoke({
            "job_description": job_description,
            "existing_info": json.dumps(existing_info, indent=2),
            "new_info": json.dumps(form_data, indent=2)
        })
    except Exception as e:
        raise ValueError(f"Failed to build resume: {str(e)}")

    # Step 3 — generate HTML
    html = build_resume_html(resume_data)


    return {
        "html": html,
        "new_fit_score": resume_data.get("fit_score", 0),
        "cover_letter": resume_data.get("cover_letter", ""),
        "cold_message": resume_data.get("cold_message", "")
    }