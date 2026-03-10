"""
Adaptador de Embeddings para AWS Bedrock
"""
import os
import boto3
from typing import Any, List, Optional
from langchain_aws import BedrockEmbeddings

from src.core.ports.embedder_provider_port import EmbeddingProviderPort
import logging

class AWSBedrockEmbeddingAdapter(EmbeddingProviderPort):
    """Implementación de Embeddings usando AWS Bedrock"""
    
    def _init_(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        region_name: str = "us-east-1"
    ):
        self.logger = logging.getLogger(f"{__name__}.AWSBedrockEmbeddingAdapter")
        
        # Usar credenciales proporcionadas o variables de entorno
        self.aws_access_key_id = aws_access_key_id or os.getenv('aws_access_key_id')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('aws_secret_access_key')
        self.aws_session_token = aws_session_token or os.getenv('aws_session_token')
        self.region_name = region_name or os.getenv('aws_region', 'us-east-1')

        self._session = None
        self._client = None
        self._embedder: Optional[BedrockEmbeddings] = None
    
    def _get_bedrock_client(self):
        """Crea y retorna el cliente de Bedrock Runtime"""
        if self._client is None:
            aws_session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token,
                region_name=self.region_name
            )
            self._session = aws_session
            self._client = aws_session.client("bedrock-runtime")
        return self._client
    
    def get_embeddings(
        self, 
        model_id: str = "amazon.titan-embed-text-v2:0",
        **kwargs
    ) -> BedrockEmbeddings:
        """
        Crea una instancia de BedrockEmbeddings
        
        Args:
            model_id: ID del modelo Bedrock (ej: "amazon.titan-embed-text-v2:0")
            **kwargs: Parámetros adicionales para BedrockEmbeddings
            
        Returns:
            BedrockEmbeddings configurado
        """
        self.logger.info(f"Creando Embeddings Bedrock con modelo: {model_id}")
        
        bedrock_client = self._get_bedrock_client()
        
        self._embedder = BedrockEmbeddings(
            client=bedrock_client,
            model_id=model_id,
            **kwargs
        )
        
        return self._embedder
    
    def embed_query(self, text: str) -> List[float]:
        """
        Genera el embedding para un texto de consulta.
        
        Args:
            text: Texto a vectorizar
            
        Returns:
            Lista de floats representando el vector de embedding
        """
        if self._embedder is None:
            self.get_embeddings()
        
        self.logger.debug(f"Generando embedding para query de {len(text)} caracteres")
        return self._embedder.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de documentos.
        
        Args:
            texts: Lista de textos a vectorizar
            
        Returns:
            Lista de vectores de embedding
        """
        if self._embedder is None:
            self.get_embeddings()
        
        self.logger.debug(f"Generando embeddings para {len(texts)} documentos")
        return self._embedder.embed_documents(texts)
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "AWS Bedrock Embeddings"
    
    def validate_credentials(self) -> bool:
        """Valida credenciales AWS"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token,
                region_name=self.region_name
            )
            sts = session.client('sts')
            sts.get_caller_identity()
            self.logger.info("Credenciales AWS validadas correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error validando credenciales AWS: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Limpia recursos AWS"""
        self._session = None
        self._client = None
        self._embedder = None
        self.logger.info("Recursos AWS Embeddings liberados")