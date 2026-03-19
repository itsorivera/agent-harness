import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.adapter.rest.rest import router as investments_router
from src.utils.logger import get_logger

# Windows (ProactorEventLoop vs SelectorEventLoop)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = get_logger(__name__)

def create_app() -> FastAPI:
    logger.info("Initializing FastAPI application")
    app = FastAPI(
        title="Agent Harness API",
        description="Agent Harness endpoints",
        version="1.0.0",
    )
    app.include_router(investments_router)


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