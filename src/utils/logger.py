import logging
import sys
import structlog
from typing import Any, Dict
import threading

# Thread-local storage for correlation_id
_context = threading.local()

def set_correlation_id(correlation_id: str):
    _context.correlation_id = correlation_id

def get_correlation_id() -> str:
    return getattr(_context, "correlation_id", "no-id")

def correlation_id_processor(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Injects correlation_id into the event_dict."""
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict

_is_configured = False

def setup_logger(json_format: bool = False):
    """
    Configures structlog and standard logging.
    """
    global _is_configured
    if _is_configured:
        return
        
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        correlation_id_processor,
    ]

    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Redirect standard logging to structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )
    _is_configured = True

def get_logger(name: str):
    if not _is_configured:
        setup_logger()
    return structlog.get_logger(name)
