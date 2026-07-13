from pydantic import BaseModel
from typing import Optional, Dict, Any

class AgentEvent(BaseModel):
    agent: str
    status: str
    data: Optional[Any] = None
    message: Optional[str] = None

class AgentStatus(BaseModel):
    agent: str
    status: str
    progress: int = 0
    details: Optional[str] = None