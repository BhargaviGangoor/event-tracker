import sys
import traceback
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from app.main import app
from app.db.session import init_db, engine
from app.db.models import Base

Base.metadata.drop_all(bind=engine)
init_db()

with TestClient(app) as client:
    try:
        client.post("/track", json={
            "userId": "user_1",
            "event": "login",
            "metadata": {"source": "web"}
        })
        print("calling analytics...")
        client.get("/analytics")
        print("Success!")
    except Exception as e:
        with open("error_trace.txt", "w") as f:
            f.write(traceback.format_exc())
