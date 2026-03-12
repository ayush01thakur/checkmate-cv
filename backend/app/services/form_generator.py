
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings
from app.schemas.enhance import FormField, DynamicForm

llm= ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key = settings.GEMINI_API_KEY,
    temperature=0.25
)

prompt = ChatPromptTemplate.from_template("""

You are a resume improvement assistant.

Based on the improvements list below, generate a dynamic form to collect missing information from the candidate.

Rules:
- Only ask for information that is relevant to the improvements listed
- Group fields by section: "projects", "experience", "skills", "achievements", "education", "summary"
- For each field specify: id, label, type, required, section, placeholder
- Field types allowed: "text", "textarea", "url", "select"
- Mark a field required=true only if it is critical to address the improvement
- Work experience section MUST always have a yes/no select field first
- Always add one optional "summary" section field at the end
- Generate fields for ANY role type — tech, non-tech, creative, finance, marketing, etc.
- Keep labels clear and human friendly
- Keep placeholders helpful with examples

Respond ONLY with raw JSON. No markdown, no explanation, no code blocks.

Format:
{{
  "fields": [
    {{
      "id": "unique_snake_case_id",
      "label": "Human readable label",
      "type": "text|textarea|url|select",
      "required": true,
      "section": "projects|experience|skills|achievements|education|summary",
      "placeholder": "Helpful example text"
    }}
  ]
}}

IMPROVEMENTS LIST:
{improvements}
""")


parser = JsonOutputParser()
chain = prompt | llm | parser


def generate_form_fields(improvements: list[str])->DynamicForm:
    """uses llm to generate dynamic form fields based on improvements required.."""

    improvements_text = "\n".join(f"- {i}" for i in improvements)

    try:
        result = chain.invoke({"improvements": improvements_text})
        fields = [FormField(**f) for f in result['fields']]

        # ensuring summary field exists at end
        has_summary = any(f.section == "summary" for f in fields)

        if not has_summary:
            fields.append(FormField(
                id="personal_summary",
                label= "Professional Summary (optional)",
                type= "textarea",
                required=False,
                section='summary',
                placeholder='2-3 lines about yourself, your goal, and what makes you a strong candidate'
            ))

        return DynamicForm(fields=fields)
    
    except Exception as e:
        raise ValueError(f"Form generation failed: {str(e)}")