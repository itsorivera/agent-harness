from fastapi import APIRouter, Depends
from typing import Annotated
from src.config.AgentDependenciesContainter import get_agent_general
from src.core.ports.agent_port import AgentPort
import uuid
from src.utils.logger import get_logger, set_correlation_id
import traceback

logger = get_logger(__name__)   
router = APIRouter(prefix="/api/v1/agents",
                   tags=["general-agent"])

@router.post(
        path="/general/query",
        description="Endpoint to query the general agent with a natural language question.")
async def query_general_agent(
    question: str,
    agent: Annotated[AgentPort, Depends(get_agent_general)]
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