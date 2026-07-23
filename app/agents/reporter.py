from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Reporter Agent in a Multi-Agent AI System.

Your responsibility:
Synthesize all insights from previous agents into ONE unified, clean, seamless Master Executive Guide tailored precisely to the user's query.

CRITICAL NON-REPETITION INSTRUCTIONS:
1. Do NOT repeat previous agent titles or sections like "Planner Agent Output", "Researcher Agent Output", "Analyst Agent Output", "Reviewer Agent Output".
2. Present a single, cohesive, highly practical final solution for the user.
3. Organize the final report into logical, topic-relevant sections (e.g., Master Roadmap, Key Requirements & Resources, Comparison & Strategy, Safety & Implementation).
4. Keep the output extremely clear, professional, well-formatted with markdown tables, bullet points, and clean headers.
"""

def reporter_agent(
    user_query: str,
    plan_output: str,
    research_output: str,
    analysis_output: str,
    review_output: str
) -> str:
    prompt = f"""User Request:
{user_query}

--- CONSOLIDATED INSIGHTS FROM COLLABORATING AGENTS ---
Planner Strategy: {plan_output}
Researcher Data: {research_output}
Analyst Matrix: {analysis_output}
Reviewer Audit: {review_output}

Generate a single unified, non-repetitive Master Executive Solution.
"""
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
