import time
import logging
from typing import Dict, Any, Callable, Optional
from app.agents.planner import planner_agent
from app.agents.researcher import researcher_agent
from app.agents.analyzer import analyzer_agent
from app.agents.reviewer import reviewer_agent
from app.agents.reporter import reporter_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MultiAgentPipeline")

def run_multi_agent_workflow(
    user_query: str,
    progress_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
) -> Dict[str, Any]:
    """
    Executes the 5-agent collaboration workflow sequentially:
    Planner -> Researcher -> Analyst -> Reviewer -> Reporter
    """
    start_time = time.time()
    results = {
        "user_query": user_query,
        "planner": "",
        "researcher": "",
        "analyst": "",
        "reviewer": "",
        "reporter": "",
        "execution_time_seconds": 0
    }

    # Step 1: Planner Agent
    logger.info("Executing 1/5: Planner Agent...")
    if progress_callback:
        progress_callback("planner_start", results)
    results["planner"] = planner_agent(user_query)
    if progress_callback:
        progress_callback("planner_done", results)

    # Step 2: Researcher Agent
    logger.info("Executing 2/5: Researcher Agent...")
    if progress_callback:
        progress_callback("researcher_start", results)
    results["researcher"] = researcher_agent(user_query, results["planner"])
    if progress_callback:
        progress_callback("researcher_done", results)

    # Step 3: Analyst Agent
    logger.info("Executing 3/5: Analyst Agent...")
    if progress_callback:
        progress_callback("analyst_start", results)
    results["analyst"] = analyzer_agent(user_query, results["planner"], results["researcher"])
    if progress_callback:
        progress_callback("analyst_done", results)

    # Step 4: Reviewer Agent
    logger.info("Executing 4/5: Reviewer Agent...")
    if progress_callback:
        progress_callback("reviewer_start", results)
    results["reviewer"] = reviewer_agent(user_query, results["planner"], results["researcher"], results["analyst"])
    if progress_callback:
        progress_callback("reviewer_done", results)

    # Step 5: Reporter Agent
    logger.info("Executing 5/5: Reporter Agent...")
    if progress_callback:
        progress_callback("reporter_start", results)
    results["reporter"] = reporter_agent(
        user_query,
        results["planner"],
        results["researcher"],
        results["analyst"],
        results["reviewer"]
    )
    if progress_callback:
        progress_callback("reporter_done", results)

    results["execution_time_seconds"] = round(time.time() - start_time, 2)
    logger.info(f"Workflow completed in {results['execution_time_seconds']} seconds.")
    
    return results
