from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Reviewer Agent in a Multi-Agent AI System.

Your responsibility:
1. Critically review the Analysis and Research provided by previous agents.
2. Check for missing considerations, safety factors, and overlooked details:
   - For **Travel & Trip Plans**: Check weather forecast risks, road safety/ghat sections, emergency medical/mechanic contacts, essential packing checklist, vehicle maintenance check, and budget emergency buffer (15%).
   - For **Other Projects**: Check safety, edge cases, legal requirements, or technical bugs.
3. Provide constructive feedback, safety guidelines, and specific risk mitigations.

Format your output with clear Markdown headers:
- ### Review Summary
- ### Identified Travel Risks & Safety Precautions
- ### Packing & Preparation Checklist
- ### Essential Recommendations
"""

def reviewer_agent(user_query: str, plan_output: str, research_output: str, analysis_output: str) -> str:
    prompt = f"""User Request:
{user_query}

Execution Plan:
{plan_output}

Research Findings:
{research_output}

Technical Analysis:
{analysis_output}

Perform a thorough quality review, identify risks/missing items, and provide packing & safety guidelines.
"""
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)


