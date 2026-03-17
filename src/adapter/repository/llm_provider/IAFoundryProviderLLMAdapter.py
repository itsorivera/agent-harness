import os
from typing import Any, Optional
from openai import AzureOpenAI
from langchain_openai import AzureChatOpenAI

from src.core.ports.llm_provider_port import LLMProviderPort
from src.utils.logger import setup_logger


class IAFoundryLLMAdapter(LLMProviderPort):
    """Implementación de LLM usando IAFoundry (Azure OpenAI)"""
    
    def _init_(
        self,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-08-01-preview",
        deployment_name: Optional[str] = None
    ):
        self.logger = setup_logger(f"{__name__}.IAFoundryLLMAdapter")
        
        # Usar credenciales proporcionadas o variables de entorno
        self.azure_endpoint = azure_endpoint or os.getenv('AZ_ENDPOINT')
        self.api_key = api_key or os.getenv('AZ_KEY')
        self.api_version = api_version
        self.deployment_name = deployment_name or os.getenv('AZ_DEPLOY')
        
        self._client = None
        
        # Validar que se tengan las credenciales necesarias
        if not self.azure_endpoint:
            self.logger.warning("Azure endpoint no configurado")
        if not self.api_key:
            self.logger.warning("Azure API key no configurada")
    
    def get_llm(
        self, 
        model_id: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AzureChatOpenAI:
        """
        Crea una instancia de AzureChatOpenAI para LangChain
        
        Args:
            model_id: Nombre del deployment en Azure (ej: "gpt-4", "gpt-35-turbo")
            temperature: Temperatura para la generación (0.0 - 2.0)
            max_tokens: Máximo de tokens en la respuesta
            **kwargs: Parámetros adicionales para Azure OpenAI
            
        Returns:
            AzureChatOpenAI configurado
        """
        self.logger.info(f"Creando LLM IAFoundry con modelo: {model_id}")
        
        # Usar el deployment_name proporcionado o el model_id
        deployment = kwargs.pop('deployment_name', model_id)
        
        # Crear instancia del LLM compatible con LangChain
        llm = AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            deployment_name=deployment,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        self.logger.info(f"LLM IAFoundry creado exitosamente con deployment: {deployment}")
        return llm
    
    def create_client(self) -> AzureOpenAI:
        """
        Crea y retorna un cliente nativo de Azure OpenAI.
        Útil para operaciones directas sin LangChain.
        
        Returns:
            AzureOpenAI: Cliente configurado
        """
        if not self._client:
            self._client = AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
            self.logger.info("Cliente nativo Azure OpenAI creado")
        return self._client
    
    def invoke_model(
        self, 
        prompt: str, 
        system_message: str = "You are a helpful assistant.",
        temperature: float = 0.7, 
        max_tokens: int = 1000,
        deployment_name: Optional[str] = None
    ) -> str:
        """
        Invoca el modelo Azure OpenAI con el prompt dado.
        Método de conveniencia para invocaciones simples.
        
        Args:
            prompt: Pregunta o prompt del usuario
            system_message: Mensaje del sistema para configurar el comportamiento
            temperature: Temperatura de muestreo (0-2). Mayor = más aleatorio
            max_tokens: Máximo de tokens en la respuesta
            deployment_name: Nombre del deployment (usa self.deployment_name si no se especifica)
            
        Returns:
            str: Texto de respuesta del modelo
        """
        client = self.create_client()
        deployment = deployment_name or self.deployment_name
        
        if not deployment:
            raise ValueError("deployment_name debe ser especificado o configurado en AZ_DEPLOY")
        
        self.logger.info(f"Invocando modelo {deployment} con prompt de {len(prompt)} caracteres")
        
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        return "IAFoundry (Azure OpenAI)"
    
    def validate_credentials(self) -> bool:
        """Valida credenciales de Azure OpenAI"""
        try:
            if not self.azure_endpoint or not self.api_key:
                self.logger.error("Credenciales incompletas: endpoint o API key faltantes")
                return False
            
            # Intentar crear un cliente y hacer una llamada simple
            client = self.create_client()
            
            # Verificar que el deployment esté disponible
            if self.deployment_name:
                test_response = client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                self.logger.info("Credenciales IAFoundry validadas correctamente")
                return True
            else:
                self.logger.warning("No se puede validar completamente sin deployment_name")
                return True  # Asumimos válido si el cliente se crea
                
        except Exception as e:
            self.logger.error(f"Error validando credenciales IAFoundry: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Limpia recursos del cliente"""
        self._client = None
        self.logger.info("Recursos IAFoundry liberados")