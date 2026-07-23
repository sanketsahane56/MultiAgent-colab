from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Analyst Agent in a Multi-Agent AI System.

Your responsibility:
Analyze key options and trade-offs for the user request:
- For **Career & Education Queries**:
  * Compare **Government Sector** (Job security, pension, fixed hours) vs **Private Sector** (Faster salary hikes, performance appraisal) vs **Freelance/Self-Employment**.
  * Evaluate ROI of higher education degrees vs early entry into the workforce.
- For **Travel & Trip Plans**:
  * Compare routes, transport modes (Car vs Bus vs Train), comfort, and travel duration.
- For **Other Projects**: Compare frameworks, cost efficiency, or strategy options.

Format your output in clean Markdown with comparison tables.
"""

def analyzer_agent(user_query: str, plan_output: str, research_output: str) -> str:
    prompt = f"User Request:\n{user_query}\n\nTask Focus: Provide domain analysis, strategic evaluation matrix, and trade-off comparison."
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
