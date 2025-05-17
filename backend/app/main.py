# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.modules.routers.sonar_router import router as sonar_router
from app.modules.routers.feedback_router import router as feedback_router

app = FastAPI(title="Autoclass AI Agent")

# CORS configuration to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Sonar scheduling routes
app.include_router(sonar_router, prefix="/sonar", tags=["Sonar"])
# Include the feedback (bug report) routes
app.include_router(feedback_router, prefix="/api", tags=["Feedback"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}