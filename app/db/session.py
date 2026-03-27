#1. Connecting to database
#2. Creating tables
#3. Giving DB session to APIs (Dependency Injection)
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.db.models import Base

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

if SUPABASE_URL:
    if SUPABASE_URL.startswith("postgresql://"):
        SUPABASE_URL = SUPABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif SUPABASE_URL.startswith("postgres://"):
        SUPABASE_URL = SUPABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
        
    SQLALCHEMY_DATABASE_URL = SUPABASE_URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "events.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}#same thread
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)#session creation

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
