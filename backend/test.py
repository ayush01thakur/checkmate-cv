from app.services.form_generator import generate_form_fields

result = generate_form_fields([
    "Add quantifiable results to your marketing campaigns",
    "Include client testimonials or case studies",
    "Highlight your experience with CRM tools like Salesforce"
])

print(f"Generated {len(result.fields)} fields")

for f in result.fields:
    print(f"  [{f.section}] {f.label} (required={f.required})")