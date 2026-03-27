import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.adapter.rest.rest import router as investments_router
from src.utils.logger import get_logger, set_correlation_id
from fastapi import Request
import uuid

logger = get_logger(__name__)

def create_app() -> FastAPI:
    logger.info("Initializing FastAPI application")
    app = FastAPI(
        title="Agent Harness API",
        description="Agent Harness endpoints",
        version="1.0.0",
    )
    
    # Enable CORS for the frontend apps
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For production, limit this to the specific Vercel URL
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(investments_router)

    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next):
        """Middleware to trace every request with a unique ID."""
        # Try to get the ID from the header (if it comes from a gateway/client)
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        
        # Set the ID in the ContextVar (safe for threads and async)
        set_correlation_id(correlation_id)
        
        # Continue with the execution of the request
        response = await call_next(request)
        
        # Return the ID in the response headers for frontend/QA debugging
        response.headers["X-Correlation-ID"] = correlation_id
        return response


    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred in the server.",
                "type": type(exc).__name__
            }
        )

    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy",
                "message": "The application is running smoothly!"}

    @app.get("/health/liveness")
    async def liveness_check():
        return {"status": "alive"}

    @app.get("/health/readiness")
    async def readiness_check():
        return {"status": "ready"}

    return app

app = create_app()