from fastapi import APIRouter, Depends, Query, HTTPException #APIRouter for api endpoints,Depends for dependency classes,Query for query parameters and HTTPException for HTTP errors
from sqlalchemy.orm import Session #sqlalcemy is connection to db and session is for creating session
from typing import Optional, List #to define optional parameters
from datetime import datetime

from app.db.session import get_db
from app.db.schemas import EventCreate, EventResponse, AnalyticsResponse, SearchEventResult, SimilarUserResponse #pydantic schema, others used for  services logic..app routers only handle apis
from app.services import event_service, analytics_service, search_service, similar_users_service

router = APIRouter() #mini app for routes

@router.post("/track", response_model=EventResponse) #tracks event,stores metadata in db and embeddings to chromadb
def create_event_record(event: EventCreate, db: Session = Depends(get_db)):
    """
    Track an event. Stores metadata in DB and generates semantic embeddings.
    """
    return event_service.track_event(db, event)

@router.get("/analytics", response_model=AnalyticsResponse) #analytics data like date and all
def get_analytics_metrics(
    event: Optional[str] = Query(None, description="Filter by event type"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Calculate from this timestamp"),
    to_date: Optional[datetime] = Query(None, alias="to", description="Calculate to this timestamp"),
    db: Session = Depends(get_db) #1. Calls get_db()
#2. Creates DB session
#3. Gives it to your function
#4. Closes it after request
):
    """
    Get aggregated usage metrics, with optional filtering.
    """
    return analytics_service.get_analytics(db, event, from_date, to_date)

@router.get("/search", response_model=List[SearchEventResult]) #search route
def search_events_semantically(
    query: str = Query(..., description="Semantic search query"),
    limit: int = Query(5, ge=1, le=100, description="Max number of results to return")
):
    """
    Returns events most semantically matched to query string via ChromaDB logic.
    """
    return search_service.search_events(query, limit=limit)

@router.get("/similar-users", response_model=List[SimilarUserResponse]) #similar users query /similar-users?userId=123
def get_similar_users(
    userId: str = Query(..., description="Target User ID"), 
    limit: int = Query(5, ge=1, le=50, description="Max number of similar users to return"),
    db: Session = Depends(get_db)
):
    """
    Find users with similar behavior using their behavior vector.
    """
    result = similar_users_service.get_similar_users(db, userId, limit=limit)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
