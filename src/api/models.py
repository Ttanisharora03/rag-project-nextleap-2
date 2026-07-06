# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User's query about ICICI Prudential mutual funds")
    fund_name: Optional[str] = Field(None, description="The specific fund name context")

class ChatResponse(BaseModel):
    answer: str
    source_url: Optional[str] = None
    last_updated: Optional[str] = None
    type: str

class HealthResponse(BaseModel):
    status: str

class SchemesResponse(BaseModel):
    schemes: List[str]
