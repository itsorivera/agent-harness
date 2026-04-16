"""
Adaptador de checkpoint para PostgreSQL (LangGraph)
"""
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import psycopg

from langgraph.checkpoint.postgres import PostgresSaver

from src.config.app_config import config
from src.core.ports.checkpointer_port import CheckpointerPort, CheckpointerPortSync
from src.utils.logger import get_logger

class PostgresCheckpointerAdapterAsync(CheckpointerPort):
    """Implementación de checkpoint usando PostgreSQL con LangGraph"""
    
    def __init__(self):
        self.logger = get_logger(f"{__name__}.PostgresCheckpointerAdapter")
        self._pool = None
        self._checkpointer = None
        
    async def get_checkpointer(self) -> Any:
        """
        Crea un checkpointer de PostgreSQL
        
        Returns:
            AsyncPostgresSaver configurado
        """
        if self._checkpointer is not None:
            return self._checkpointer
            
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }
        
        postgres_uri = self._build_postgres_uri()
        self.logger.info(f"Conectando a PostgreSQL checkpoint")
        
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

class PostgresCheckpointerAdapterSync(CheckpointerPortSync):
    """Implementación de checkpoint usando PostgreSQL con LangGraph (sincronía)"""

    def __init__(self):
        self.logger = get_logger(f"{__name__}.PostgresCheckpointerAdapterSync")
        self._conn = None

    def get_checkpointer(self):
        """
        Crea un checkpointer de PostgreSQL

        Returns:
            PostgresSaver configurado
        """
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }

        postgres_uri = self._build_postgres_uri()
        self.logger.info(f"Conectando a PostgreSQL checkpoint")

        # Mantener la conexión abierta para uso persistente
        self._conn = psycopg.connect(postgres_uri, **connection_kwargs)
        checkpointer = PostgresSaver(self._conn)
        
        # Crear las tablas si no existen
        checkpointer.setup()
        
        return checkpointer

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

    def cleanup(self) -> None:
        """Limpia recursos de PostgreSQL"""
        if self._conn:
            self._conn.close()