import uvicorn
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Fix for Psycopg + Windows (ProactorEventLoop compatibility)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(
        "src.app:app",
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", 8000)),
    )
