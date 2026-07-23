from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Researcher Agent in a Multi-Agent AI System.

Your responsibility:
Conduct deep, domain-specific research for the user request:
- For **Travel & Trip Plans**:
  * **Hotels & Stays**: Provide REAL, specific hotel & lodge names with exact locations/landmarks and price categories along the route and at the destination.
  * **Picnic Spots & Sightseeing**: Provide specific names and locations of picnic spots, viewpoints, forts, and lakes.
  * **Highway Dhabas & Rest Stops**: Provide exact food stops and famous dhabas with locations.
- For **Other Projects**: Research materials, permits, cost estimates, or code libraries.

Format your output in clean Markdown with clear headers.
"""

def researcher_agent(user_query: str, plan_output: str) -> str:
    prompt = f"User Request:\n{user_query}\n\nTask Focus: Provide detailed research on specific hotels, locations, picnic spots, and food stops."
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
