from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Reviewer Agent in a Multi-Agent AI System.

Your responsibility:
Conduct safety, eligibility, and quality assurance audits for the user request:
- For **Career & Education Queries**:
  * Audit degree recognition (NCTE, UGC, AICTE, NMC, BCI verified universities).
  * Check age relaxation rules, mandatory entrance test cutoff requirements, and common pitfalls to avoid.
- For **Travel & Trip Plans**:
  * Audit vehicle condition, ghat driving precautions, hotel confirmation, and emergency contacts.

Format your output with clean markdown checklists and audit decision.
"""

def reviewer_agent(user_query: str, plan_output: str, research_output: str, analysis_output: str) -> str:
    prompt = f"User Request:\n{user_query}\n\nTask Focus: Provide eligibility audit, accreditation verification, safety checklist, and approval decision."
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
