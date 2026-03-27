#Pydantic = tool that validates and structures data automatically
from pydantic import BaseModel, ConfigDict #basemodel is base for all classes and configdict is to configure schema behavior
from typing import Dict, Any, Optional, List #the 4 data types
from datetime import datetime

class EventCreate(BaseModel):
    userId: str
    event: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None

class EventResponse(BaseModel): #depends on EventCreate
    id: str
    userId: str
    event: str
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime

    model_config = ConfigDict(populate_by_name=True, from_attributes=True) #Convert SQLAlchemy object → Pydantic automatically

class AnalyticsResponse(BaseModel):
    total_events: int
    events_per_user: Dict[str, int]
    most_active_users: List[Dict[str, Any]]

class SearchEventResult(BaseModel):
    distance: Optional[float] = None
    event: EventResponse

class SimilarUserResponse(BaseModel):
    userId: str
    similarityScore: float
