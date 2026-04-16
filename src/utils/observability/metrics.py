import time
import functools
import inspect
from typing import Any, Callable
from src.utils.logger import get_logger

logger = get_logger(__name__)

def track_latency(name: str):
    """
    Decorator to measure and log the latency of a function call.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                latency = end_time - start_time
                logger.info(f"Latencia detectada en {name}", 
                           operation=name, 
                           latency_seconds=round(latency, 4))
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                latency = end_time - start_time
                logger.info(f"Latencia detectada en {name}", 
                           operation=name, 
                           latency_seconds=round(latency, 4))
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

def track_tool_usage(tool_name: str):
    """
    Decorator to track when a tool is being used.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"Ejecutando herramienta: {tool_name}", tool=tool_name)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
