from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class Decision(BaseModel):
    id: Optional[str] = Field(None, description="The unique ID of the tool call to review.")
    name: Optional[str] = Field(None, description="The name of the tool call to review.")
    type: str = Field(..., description="Action to take: 'approve', 'edit', or 'reject'.")
    edited_args: Optional[Dict[str, Any]] = Field(None, description="New arguments if type is 'edit'.")
    message: Optional[str] = Field(None, description="Clarification message if type is 'reject'.")

class QueryRequest(BaseModel):
    question: Optional[str] = None
    thread_id: str
    user_id: str
    decisions: Optional[List[Decision]] = None
    stream: bool = False

