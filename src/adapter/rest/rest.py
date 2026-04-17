from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from src.config.agent_dependencies_container import get_agent_general, get_financial_advisor_agent
from src.core.ports.agent_port import AgentPort
from src.utils.logger import get_logger, set_context_vars, get_correlation_id
from .schemas import QueryRequest

logger = get_logger(__name__)

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
        # Inject user_id into the logging context for better traceability
        set_context_vars(user_id=request.user_id)
        logger.info("New query request", thread_id=request.thread_id)
        
        response = await agent.process_message(
            message=request.question, 
            thread_id=request.thread_id,
            user_id=request.user_id,
            decisions=request.decisions
        )
        return {
            "response": response, 
            "correlation_id": get_correlation_id()
        }
    except Exception as e:
        logger.error(f"Error processing general agent query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )
    
@router.post(
        path="/financial-advisor/query",
        description="Endpoint to query the financial advisor agent with a natural language question.")
async def query_financial_advisor_agent(
    request: QueryRequest,
    agent: Annotated[AgentPort, Depends(get_financial_advisor_agent)]
    ):
    try:
        # Inject user_id into the logging context for better traceability
        set_context_vars(user_id=request.user_id)
        logger.info("New financial advisor query request", thread_id=request.thread_id)
        
        response = await agent.process_message(
            message=request.question, 
            thread_id=request.thread_id,
            user_id=request.user_id,
            decisions=request.decisions
        )
        return {
            "response": response, 
            "correlation_id": get_correlation_id()
        }
    except Exception as e:
        logger.error(f"Error processing financial advisor query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )
