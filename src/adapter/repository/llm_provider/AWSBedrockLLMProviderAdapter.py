from src.core.ports.llm_provider_port import LLMProviderPort
from typing import Optional
from langchain_aws import ChatBedrockConverse
import traceback
import boto3
import os

class AWSLLMProviderAdapter(LLMProviderPort):
  def __init__(self, 
               aws_access_key_id: Optional[str] = None,
               aws_secret_access_key: Optional[str] = None,
               aws_session_token: Optional[str] = None,
               aws_region: Optional[str] = None):
    self.aws_access_key_id = aws_access_key_id or os.getenv('aws_access_key_id')
    self.aws_secret_access_key = aws_secret_access_key or os.getenv('aws_secret_access_key')
    self.aws_session_token = aws_session_token or os.getenv('aws_session_token')
    self.aws_region = aws_region or os.getenv('aws_region', 'us-east-1')

    self._session = None
    self._client = None
 
  def get_llm(self,
              model_id,
              **kwargs) -> ChatBedrockConverse:
    
    if self._client is None:
      print("Inicializating bedrock client")
      self._session = boto3.Session(
        aws_access_key_id=self.aws_access_key_id,
        aws_secret_access_key=self.aws_secret_access_key,
        aws_session_token=self.aws_session_token,
        region_name=self.aws_region
      )
      self._client = self._session.client('bedrock-runtime')
    
    llm = ChatBedrockConverse(
      client=self._client,
      model=model_id,
      **kwargs,
    )

    return llm

  def validate_credentials(self):
    try:
      self._session = boto3.Session(
        aws_access_key_id=self.aws_access_key_id,
        aws_secret_access_key=self.aws_secret_access_key,
        aws_session_token=self.aws_session_token,
        region_name=self.aws_region
      )
      self._client = self._session.client('bedrock-runtime')
      print("Credentials validated successfully")
      return True
    except Exception as e:
      print(f"Error validating credentials: {str(e)}")
      traceback.print_exc()
      return False
  
  def cleanup(self):
    self._session = None
    self._client = None
    print("AWS Bedrock client cleaned up")

  def get_provider_name(self) -> str:
    return "AWS Bedrock (AWS LLM Provider)"

