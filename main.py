import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import settings
from core.scheduler import start_scheduler, stop_scheduler
from api.v1.api_router import api_router
from core.database import engine
from models import Base

# Create all tables in the database
Base.metadata.create_all(bind=engine)


# ── App Lifespan (startup + shutdown) ────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins for testing locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve static files for returning image urls
import os
os.makedirs("uploads/scans", exist_ok=True)
app.mount("/static/scans", StaticFiles(directory="uploads/scans"), name="static")
os.makedirs("uploads/profiles", exist_ok=True)
app.mount("/static/profiles", StaticFiles(directory="uploads/profiles"), name="profiles")
os.makedirs("exports", exist_ok=True)
app.mount("/static/exports", StaticFiles(directory="exports"), name="exports")

@app.get("/")
def root():
    return {"message": "Welcome to UltraXpert Backend API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
