import numpy as np
from typing import List, Dict, Union
from sqlalchemy.orm import Session
from collections import defaultdict
from functools import lru_cache

from app.db.models import Event
from app.db.vector_db import events_collection

@lru_cache(maxsize=1000)
def _get_cached_user_vector(user_id: str, event_ids_tuple: tuple) -> np.ndarray:
    """
    Fetches and computes the normalized mean vector for a user.
    Uses a tuple of event_ids for cacheability.
    """
    if not event_ids_tuple:
        return None
        
    # Fetch embeddings array for specific user from Chroma
    res = events_collection.get(
        ids=list(event_ids_tuple),
        include=["embeddings"]
    )
    
    vectors = res.get("embeddings", [])
    
    # Handle empty or invalid returns safely
    if not vectors or len(vectors) == 0:
        return None
        
    # Convert safely to numpy array
    try:
        vec_array = np.array(vectors, dtype=float)
    except Exception:
        return None
        
    # Safe check for empty NumPy array to avoid "truth value ambiguous" exceptions
    if vec_array.size == 0:
        return None

    # Handle single vs multiple vectors natively
    # If 1D, it remains 1D. If 2D (multiple events), we average along axis 0.
    if vec_array.ndim > 1:
        avg_vec = np.mean(vec_array, axis=0)
    else:
        avg_vec = vec_array
        
    # Normalize the vector automatically (L2 norm)
    norm = np.linalg.norm(avg_vec)
    if norm == 0:
        return None
        
    return avg_vec / norm

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Computes exact cosine similarity safely."""
    if v1 is None or v2 is None:
        return 0.0
        
    dot_prod = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return float(dot_prod / (norm_v1 * norm_v2))

def get_similar_users(db: Session, user_id: str, limit: int = 5) -> Union[List[Dict[str, Union[str, float]]], Dict[str, str]]:
    """
    Identifies users with similar behavior patterns via Chroma Vector space using Cosine Similarity.
    """
    # 1. Fetch relational mappings
    all_events = db.query(Event.id, Event.user_id).all()
    
    user_event_ids = defaultdict(list)
    for eid, uid in all_events:
        user_event_ids[uid].append(eid)
        
    if user_id not in user_event_ids:
        return {"error": f"User {user_id} not found or has no events"}

    # 2. Get Normalized Target Vector
    # Convert list to tuple to make it hashable for lru_cache
    target_tuple = tuple(user_event_ids[user_id])
    target_user_vec = _get_cached_user_vector(user_id, target_tuple)
    
    if target_user_vec is None:
        return {"error": "No meaningful behavioral vectors derived for the target user"}

    similarities = []
    
    # 3. Iterate and compare against all other users
    for uid, eids in user_event_ids.items():
        if uid == user_id:
            continue
            
        uid_tuple = tuple(eids)
        u_vec = _get_cached_user_vector(uid, uid_tuple)
        
        if u_vec is None:
            continue
            
        # 4. Compute proper cosine similarity
        sim = cosine_similarity(target_user_vec, u_vec)
        
        # 5. Remove negative/meaningless matches (threshold > 0.3)
        if sim > 0.3:
            similarities.append({
                "userId": uid,
                "similarityScore": round(sim, 4)
            })
            
    # 6. Sort results descending
    similarities.sort(key=lambda x: x["similarityScore"], reverse=True)
    
    # 7. Apply Limit
    return similarities[:limit]

