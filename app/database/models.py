from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    title: str = Field(index=True)
    
    story_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)