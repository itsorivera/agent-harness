"""
Adaptador de memoria a corto plazo usando PostgreSQL (LangGraph)
"""
import os
from typing import Any
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import AsyncConnectionPool
import psycopg

from src.config.app_config import config
from src.core.ports.short_term_memory_port import ShortTermMemoryPort, ShortTermMemoryPortSync
from src.utils.logger import get_logger

class PostgresShortTermMemoryAdapter(ShortTermMemoryPort):
    """Implementación de STM usando PostgreSQL con LangGraph"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.PostgresShortTermMemoryAdapter")
        self._pool = None
        self._checkpointer = None
        
    async def get_state_manager(self) -> Any:
        """
        Crea un gestor de estado (checkpointer) de PostgreSQL
        """
        if self._checkpointer is not None:
            return self._checkpointer
            
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }
        
        postgres_uri = self._build_postgres_uri()
        self.logger.info(f"Conectando a PostgreSQL para STM")
        
        self._pool = AsyncConnectionPool(postgres_uri, kwargs=connection_kwargs, open=False)
        await self._pool.open()
        
        self._checkpointer = AsyncPostgresSaver(self._pool)
        await self._checkpointer.setup()
        
        return self._checkpointer
    
    def _build_postgres_uri(self) -> str:
        """Construye la URI de conexión a PostgreSQL"""
        if config.POSTGRES_CONNECTION_STRING:
            return config.POSTGRES_CONNECTION_STRING
            
        return (
            f"postgresql://{config.POSTGRES_USER}:"
            f"{config.POSTGRES_PASSWORD}@"
            f"{config.POSTGRES_HOST}:"
            f"{config.POSTGRES_PORT}/"
            f"{config.POSTGRES_DATABASE}?"
            f"options=-csearch_path%3D{config.CONVERSATION_SCHEMA}"
        )
    
    async def cleanup(self) -> None:
        """Limpia recursos de PostgreSQL"""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._checkpointer = None

class PostgresShortTermMemoryAdapterSync(ShortTermMemoryPortSync):
    """Implementación de STM usando PostgreSQL (Sincrónico)"""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.PostgresShortTermMemoryAdapterSync")
        self._conn = None

    def get_state_manager(self) -> Any:
        """
        Crea un gestor de estado de PostgreSQL
        """
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }

        postgres_uri = self._build_postgres_uri()
        self.logger.info(f"Conectando a PostgreSQL para STM (Sync)")

        self._conn = psycopg.connect(postgres_uri, **connection_kwargs)
        checkpointer = PostgresSaver(self._conn)
        checkpointer.setup()
        
        return checkpointer

    def _build_postgres_uri(self) -> str:
        if config.POSTGRES_CONNECTION_STRING:
            return config.POSTGRES_CONNECTION_STRING
            
        return (
            f"postgresql://{config.POSTGRES_USER}:"
            f"{config.POSTGRES_PASSWORD}@"
            f"{config.POSTGRES_HOST}:"
            f"{config.POSTGRES_PORT}/"
            f"{config.POSTGRES_DATABASE}?"
            f"options=-csearch_path%3D{config.CONVERSATION_SCHEMA}"
        )

    def cleanup(self) -> None:
        if self._conn:
            self._conn.close()