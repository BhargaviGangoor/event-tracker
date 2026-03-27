from fastapi import FastAPI #FastAPI import /backend framework
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager #used for setup and logic

from app.api.endpoints import router #api routes -- brings all api endpoints to this main app
from app.db.session import init_db #connects posgresql and database

@asynccontextmanager #function managing shutdown and start lifecycle in this app
async def lifespan(app: FastAPI):#runs before app staarts and after app ends
    # Initialize DB during startup
    init_db() #creates and initializes db in my posgresql supabase db
    yield

app = FastAPI(
    title="Intelligent Event Tracker API",
    description="Event Tracking with Semantic Search and Basic Analytics",
    version="1.0.0",
    lifespan=lifespan #lifespan means
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins; update securely for production
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

app.include_router(router) #attaches urls to the app
