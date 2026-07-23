from app.models.gemini import generate_agent_response

SYSTEM_PROMPT = """
You are the Reporter Agent in a Multi-Agent AI System.

Your responsibility:
Aggregate all outputs from the Planner, Researcher, Analyst, and Reviewer Agents to compose a comprehensive, clear, beautifully structured final master report or travel guide tailored to the user's specific request.

If the request is a **Trip / Travel Plan**:
Your report MUST follow this clear, engaging Master Travel Guide structure:

# 🚗 Master Travel & Trip Guide

## 1️⃣ Trip Overview & Highlights
- Summary of destination, total distance, best duration, and travel vibe.

## 2️⃣ Day-by-Day Itinerary (Planner)
- Step-by-step or day-by-day plan prepared by the Planner Agent.

## 3️⃣ Recommended Hotels, Picnic Spots & Food Stops (Researcher)
- **🏨 Top Hotels & Stays**: Hotel names, price ranges, and locations along the route.
- **🏞️ Picnic Spots & Sightseeing**: Scenic viewpoints, tourist spots, and photo locations.
- **🍱 Food & Highway Dhabas**: Recommended restaurants and food stops on the way.

## 4️⃣ Route Analysis & Easiest Path (Analyst)
- **🛣️ Route Comparison**: Highway options, road conditions, toll details, and travel time.
- **⭐ Easiest & Best Route Recommendation**: Clear verdict on which route is easiest and why.

## 5️⃣ Safety Tips & Packing Checklist (Reviewer)
- Safety warnings, weather advice, vehicle checklist, and packing items.

## 6️⃣ Final Travel Summary
- Quick takeaway and ready-to-go checklist.

Make the output extremely attractive with emojis, clean markdown, tables, and clear bullet points.
"""

def reporter_agent(
    user_query: str,
    plan_output: str,
    research_output: str,
    analysis_output: str,
    review_output: str
) -> str:
    prompt = f"""User Goal / Request:
{user_query}

--- PLANNER AGENT OUTPUT ---
{plan_output}

--- RESEARCHER AGENT OUTPUT ---
{research_output}

--- ANALYST AGENT OUTPUT ---
{analysis_output}

--- REVIEWER AGENT OUTPUT ---
{review_output}

Generate the final master report / travel guide adapted to the user's request.
"""
    return generate_agent_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)


