# backend/app/modules/routers/feedback_router.py

import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

router = APIRouter()

# where to append feedback
FEEDBACK_LOG = os.getenv("FEEDBACK_LOG_PATH", "feedback.log")

class FeedbackRequest(BaseModel):
    page: str = Field(..., description="The front-end route where the bug occurred")
    title: str = Field(..., min_length=5, description="Short summary of the issue")
    description: str = Field(..., min_length=10, description="Detailed description or steps to reproduce")
    email: Optional[EmailStr] = Field(None, description="Your email (optional)")

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    """Append bug report to a JSONL logfile."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "page": req.page,
        "title": req.title,
        "description": req.description,
        "email": req.email,
    }
    try:
        with open(FEEDBACK_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write feedback: {e}")
    return {"status": "ok", "message": "Thank you! Your report has been submitted."}