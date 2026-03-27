from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Event
from typing import Optional
from datetime import datetime

def get_analytics(
    db: Session, 
    event_type: Optional[str] = None, 
    from_date: Optional[datetime] = None, 
    to_date: Optional[datetime] = None
) -> dict:
    
    def apply_filters(query):
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if from_date:
            query = query.filter(Event.timestamp >= from_date)
        if to_date:
            query = query.filter(Event.timestamp <= to_date)
        return query

    # Base query for aggregation
    base_query = apply_filters(db.query(Event))
    total_events = base_query.count()
    
    # Query for grouping metrics
    user_counts_query = apply_filters(db.query(Event.user_id, func.count(Event.id).label('count')))
    user_counts_results = user_counts_query.group_by(Event.user_id).order_by(func.count(Event.id).desc()).all()
    
    events_per_user = {row.user_id: row.count for row in user_counts_results}
    
    # Return top 10 most active users directly from the grouped query
    most_active_users = [{"userId": row.user_id, "count": row.count} for row in user_counts_results[:10]]
    
    return {
        "total_events": total_events,
        "events_per_user": events_per_user,
        "most_active_users": most_active_users
    }
