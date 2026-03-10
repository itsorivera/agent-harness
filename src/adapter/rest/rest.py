from fastapi import APIRouter, Depends
from typing import Annotated
from src.config.AgentDependenciesContainter import get_agent_investment_root
from src.core.ports.agent_port import AgentPort
import uuid
from src.utils.logger import set_correlation_id, get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/investments",
                   tags=["investments"])

@router.post(
        path="/query",
        description="Endpoint to query the investment research agent with a natural language question about investors, companies, industries or news.")
async def query_investment_agent(
    question: str,
    agent: Annotated[AgentPort, Depends(get_agent_investment_root)]
    ):
    try:
        correlation_id = str(uuid.uuid4())
        set_correlation_id(correlation_id)
        logger.info("New query request", question=question, correlation_id=correlation_id)
        
        response = await agent.process_message(question, "abc-01")
        return {"response": response, "correlation_id": correlation_id}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}