from abc import ABC, abstractmethod
from typing import Any, List


class EmbeddingProviderPort(ABC):
    """
    Puerto abstracto para implementaciones de proveedores de Embeddings.
    
    Define el contrato que deben cumplir los adaptadores de Embeddings
    (e.g., AWS Bedrock, OpenAI, Cohere, etc.)
    """
    
    @abstractmethod
    def get_embeddings(
        self, 
        model_id: str,
        **kwargs
    ) -> Any:
        """
        Crea y retorna una instancia del modelo de embeddings configurado.
        
        Args:
            model_id: Identificador del modelo (específico del proveedor)
            **kwargs: Parámetros adicionales específicos del proveedor
            
        Returns:
            Una instancia del modelo de embeddings configurada y lista para usar
            
        Ejemplo:
            embedder = adapter.get_embeddings(
                model_id="amazon.titan-embed-text-v2:0"
            )
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Genera el embedding para un texto de consulta.
        
        Args:
            text: Texto a vectorizar
            
        Returns:
            Lista de floats representando el vector de embedding
        """
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de documentos.
        
        Args:
            texts: Lista de textos a vectorizar
            
        Returns:
            Lista de vectores de embedding
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Retorna el nombre del proveedor de Embeddings.
        
        Returns:
            Nombre del proveedor (e.g., "AWS Bedrock", "OpenAI", "Cohere")
        """
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Valida las credenciales del proveedor.
        
        Returns:
            True si las credenciales son válidas, False en caso contrario
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Limpia recursos y conexiones del proveedor de Embeddings.
        """
        pass