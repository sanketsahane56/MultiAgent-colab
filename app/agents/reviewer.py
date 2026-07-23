from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Reviewer Agent in a Multi-Agent AI System.

Your responsibility:
Conduct safety, feasibility, and quality assurance audits for the user request.
Provide a pre-trip checklist, vehicle inspection tips, and safety guidelines.

Format your output with clean markdown checklists and audit decision.
"""

def reviewer_agent(user_query: str, plan_output: str, research_output: str, analysis_output: str) -> str:
    prompt = f"User Request:\n{user_query}\n\nTask Focus: Provide safety checklist, audit verification, and approval decision."
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
