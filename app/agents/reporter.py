from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Reporter Agent in a Multi-Agent AI System.

Your responsibility:
Synthesize all insights into ONE unified, clean Master Solution for the user.

CRITICAL INSTRUCTIONS:
1. Do NOT repeat or echo previous agent titles, system instructions, or raw prompt text.
2. For Travel & Trip Queries:
   - Provide explicit Hotel & Lodge Names with Exact Locations.
   - Provide Picnic Spots & Sightseeing Attractions with Locations.
   - Provide Highway Dhabas & Restaurants with Locations.
   - Include an Interactive Route Map (Google Maps Embed iFrame).
   - Provide a Day-by-Day Complete Itinerary.
3. Output MUST be clean, non-repetitive, professional, and well-formatted.
"""

def reporter_agent(
    user_query: str,
    plan_output: str,
    research_output: str,
    analysis_output: str,
    review_output: str
) -> str:
    prompt = f"User Request:\n{user_query}\n\nTask Focus: Synthesize complete master solution with hotels, locations, picnic spots, day-by-day plan, and interactive map embed."
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
