from pydantic import BaseModel

class AgentPersonality(BaseModel):
    tone: str
    style: str

GENERAL_AGENT_PERSONALITY = AgentPersonality(
    tone="emphatic",
    style="concise and clear"
)
