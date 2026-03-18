from typing import Optional, TypeVar, List
from src.config.app_config import config
from src.utils.logger import get_logger

logger = get_logger("config_resolver")

T = TypeVar('T')


def resolve_with_default(value: Optional[T], default: T, field_name: str = "value") -> T:
    if value is None:
        logger.debug(f"{field_name} no definido, usando default: {default}")
        return default
    return value


def resolve_model_id(model_id: Optional[str] = None) -> str:
    return resolve_with_default(
        value=model_id,
        default=config.DEFAULT_LLM_MODEL,
        field_name="model_id"
    )


def resolve_llm_provider(provider: Optional[str] = None) -> str:
    resolved = resolve_with_default(
        value=provider,
        default=config.DEFAULT_LLM_PROVIDER,
        field_name="llm_provider"
    )
    
    if resolved not in config.VALID_LLM_PROVIDERS:
        valid_providers = ", ".join(config.VALID_LLM_PROVIDERS)
        raise ValueError(
            f"LLM provider '{resolved}' no válido. "
            f"Providers válidos: {valid_providers}"
        )
    
    return resolved