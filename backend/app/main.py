import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.routers import auth, documents, chat, solutions, battlecards, conversations
from app.seed.init_data import seed_database

def background_initial_seed():
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        print(f"Background seeding notice: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Create tables if not exist
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed initial sample data in non-blocking thread so server starts immediately
    thread = threading.Thread(target=background_initial_seed, daemon=True)
    thread.start()
        
    print(f"=== {settings.APP_NAME} v{settings.APP_VERSION} Started Successfully ===")
    yield
    print(f"=== {settings.APP_NAME} Shutting Down ===")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise AI Assistant for Security Presales Architects & Solution Engineers",
    lifespan=lifespan
)

# CORS Configuration for Vercel & Localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(solutions.router)
app.include_router(battlecards.router)
app.include_router(conversations.router)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
