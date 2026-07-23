from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Analyst Agent in a Multi-Agent AI System.

Your responsibility:
Analyze key options and trade-offs for the user request:
- For **Travel & Trip Plans**:
  * **Route Analysis**: Compare alternative transport modes (Self-drive car vs Bus vs Train).
  * **Comfort & Budget**: Evaluate travel duration, road conditions, and recommend the easiest and best route.
- For **Other Projects**: Compare frameworks, cost efficiency, or strategy options.

Format your output in clean Markdown with comparison tables.
"""

def analyzer_agent(user_query: str, plan_output: str, research_output: str) -> str:
    prompt = f"User Request:\n{user_query}\n\nTask Focus: Provide route analysis, transport comparison matrix, and trade-off evaluation."
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
