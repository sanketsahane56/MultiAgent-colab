from app.workflows.pipeline import run_multi_agent_workflow

def main():
    print("[START] Testing 5-Agent Multi-Agent Collaboration Workflow...")
    query = "Build an AI chatbot using Streamlit and Gemini API"
    
    result = run_multi_agent_workflow(query)
    
    print("\n--- WORKFLOW EXECUTION COMPLETE ---")
    print(f"Time Taken: {result['execution_time_seconds']}s")
    print(f"Planner Output Length: {len(result['planner'])} chars")
    print(f"Researcher Output Length: {len(result['researcher'])} chars")
    print(f"Analyst Output Length: {len(result['analyst'])} chars")
    print(f"Reviewer Output Length: {len(result['reviewer'])} chars")
    print(f"Reporter Output Length: {len(result['reporter'])} chars")

    assert len(result["planner"]) > 50, "Planner output is empty!"
    assert len(result["researcher"]) > 50, "Researcher output is empty!"
    assert len(result["analyst"]) > 50, "Analyst output is empty!"
    assert len(result["reviewer"]) > 50, "Reviewer output is empty!"
    assert len(result["reporter"]) > 50, "Reporter output is empty!"
    
    print("\n[OK] ALL 5 AGENTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

