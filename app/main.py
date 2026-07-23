import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.workflows.pipeline import run_multi_agent_workflow
from app.models.gemini import generate_agent_response

app = FastAPI(
    title="Multi-Agent Collaboration System",
    description="5 AI Agents (Planner, Researcher, Analyst, Reviewer, Reporter) collaborating to solve complex user requests.",
    version="1.0.0"
)

class RequestPayload(BaseModel):
    query: str

@app.get("/api/health")
def health_check():
    try:
        test_response = generate_agent_response("Respond with 'OK'")
        return {
            "status": "healthy",
            "model_status": "connected",
            "sample_response": test_response.strip()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/api/run")
def run_workflow(payload: RequestPayload):
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        result = run_multi_agent_workflow(payload.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

# Serve Web Dashboard Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    def serve_dashboard():
        return FileResponse(os.path.join(frontend_path, "index.html"))