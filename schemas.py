from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TicketCreate(BaseModel):
    customer_name: str = "Unknown Customer"
    customer_email: str | None = None
    subject: str = Field(min_length=3, max_length=500)
    description: str = Field(min_length=3, max_length=20000)
    source: str = "web"
    priority: str | None = None
    auto_analyze: bool = True

class TicketUpdate(BaseModel):
    subject: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    agent_id: str | None = None
    tags: list[str] | None = None

class MessageCreate(BaseModel):
    sender_type: str = "customer"
    sender_name: str = "Customer"
    body: str = Field(min_length=1, max_length=20000)

class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    external_id: str | None
    customer_name: str
    customer_email: str | None
    subject: str
    description: str
    status: str
    priority: str
    category: str
    subcategory: str
    sentiment: str
    sentiment_score: float
    sla_risk: float
    ai_confidence: float
    agent_id: str | None
    source: str
    tags: list
    ai_summary: str | None
    recommended_action: str | None
    created_at: datetime
    updated_at: datetime

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    name: str
    role: str
    active: bool
    skills: list

class AnalyzeOut(BaseModel):
    ticket: TicketOut
    classification: dict
    priority: dict
    sentiment: dict
    sla: dict
    routing: dict
    llm: dict
