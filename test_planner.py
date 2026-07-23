from app.agents.planner import planner_agent

query = "Build an AI chatbot using Streamlit and Gemini API"

result = planner_agent(query)

print(result)