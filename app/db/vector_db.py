#chromadb connection
'''1. Converting text → vectors (embeddings)
2. Storing them in a vector database (ChromaDB)
3. Enabling semantic search
'''
import os
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
'''documents -->list of text, embeddings -->list of vectors embedding fucntions ->custon embeddign class'''
import hashlib
import numpy as np

PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")#create folder path

client = chromadb.PersistentClient(path=os.path.abspath(PERSIST_DIR))#Creates a persistent vector database
#Data is saved even after server restart

class MockEmbeddingFunction(EmbeddingFunction):
    """
    A custom embedding function that prevents ChromaDB from downloading 
    the 90MB sentence-transformers model. It generates a deterministic 
    64-dimensional mock vector based on the hash of the text snippet.
    """
    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            hash_val = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
            '''Convert text → bytes
Apply MD5 hash
Convert to integer'''
            seed = hash_val % (2**32 - 1)#Ensures seed fits within valid range
            np.random.seed(seed)
            vec = np.random.randn(64)
            norm = np.linalg.norm(vec)#Calculates vector length
            if norm > 0:
                vec = vec / norm#Normalization
            embeddings.append(vec.tolist())
        return embeddings

events_collection = client.get_or_create_collection(
    name="events",
    embedding_function=MockEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"}#Defines similarity metric
)
