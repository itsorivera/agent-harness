from fastapi import APIRouter, Depends
from typing import Annotated
from src.config.AgentDependenciesContainter import get_agent_general
from src.core.ports.agent_port import AgentPort
import uuid
from src.utils.logger import get_logger, set_context_vars, get_correlation_id
from pydantic import BaseModel
import traceback

logger = get_logger(__name__)   

class QueryRequest(BaseModel):
    question: str
    user_id: str

router = APIRouter(prefix="/api/v1/agents",
                   tags=["general-agent"])

@router.post(
        path="/general/query",
        description="Endpoint to query the general agent with a natural language question.")
async def query_general_agent(
    request: QueryRequest,
    agent: Annotated[AgentPort, Depends(get_agent_general)]
    ):
    try:
        # Inyectamos el user_id al contexto
        set_context_vars(user_id=request.user_id)
        logger.info("New query request", question=request.question)
        
        response = await agent.process_message(request.question, request.user_id)
        return {
            "response": response, 
            "correlation_id": get_correlation_id()
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}