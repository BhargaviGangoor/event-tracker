import json
from app.db.vector_db import events_collection

def search_events(query: str, limit: int = 5):
    # Chroma handles string embeddings automatically under the hood via sentence-transformers
    results = events_collection.query(
        query_texts=[query],
        n_results=limit
    )
    
    formatted_results = []
    
    # Chroma returns matching lists nested e.g. ids[0][0], distances[0][0], metadatas[0][0]
    if results['ids'] and len(results['ids'][0]) > 0:
        for idx in range(len(results['ids'][0])):
            meta = results['metadatas'][0][idx]
            
            # Reconstruct complex objects natively
            reconstructed_metadata = None
            if "stored_metadata" in meta:
                reconstructed_metadata = json.loads(meta["stored_metadata"])
                
            payload = {
                "id": results['ids'][0][idx],
                "userId": meta.get("userId"),
                "event": meta.get("event"),
                "metadata": reconstructed_metadata,
                "timestamp": meta.get("timestamp")
            }
            
            # Chroma distances with cosine: lower distance = higher similarity
            formatted_results.append({
                "distance": results['distances'][0][idx] if 'distances' in results and results['distances'] else None,
                "event": payload
            })
            
    return formatted_results
