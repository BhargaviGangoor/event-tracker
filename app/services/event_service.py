from sqlalchemy.orm import Session
from app.db.models import Event
from app.db.schemas import EventCreate, EventResponse
from app.db.vector_db import events_collection
from datetime import datetime
import json

def track_event(db: Session, event_in: EventCreate) -> EventResponse:
    # 1. Store in standard SQL DB
    timestamp = event_in.timestamp or datetime.utcnow()
    db_event = Event(
        user_id=event_in.userId,
        event_type=event_in.event,
        metadata_=event_in.metadata,
        timestamp=timestamp
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # 2. Compute text baseline for Chroma to embed natively
    text_to_embed = f"User {event_in.userId} performed {event_in.event}"
    if event_in.metadata:
        text_to_embed += f" with metadata {json.dumps(event_in.metadata, sort_keys=True)}"

    # 3. Store in Vector DB. Chroma metadata values must be primitive.
    metadata_payload = {
        "userId": db_event.user_id,
        "event": db_event.event_type,
        "timestamp": db_event.timestamp.isoformat()
    }
    if db_event.metadata_:
        metadata_payload["stored_metadata"] = json.dumps(db_event.metadata_)

    events_collection.add(
        documents=[text_to_embed],
        metadatas=[metadata_payload],
        ids=[db_event.id]#Links:Vector DB ↔ SQL DB
    )

    return EventResponse(
        id=db_event.id,
        userId=db_event.user_id,
        event=db_event.event_type,
        metadata=db_event.metadata_,
        timestamp=db_event.timestamp
    )
