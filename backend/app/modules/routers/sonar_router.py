# backend/app/modules/routers/sonar_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Import your wrapper
from app.modules.scheduler import Scheduler

router = APIRouter()
sched = Scheduler()

class ScheduleRequest(BaseModel):
    completed_courses:         List[str] = Field(..., alias="completed_courses")
    origin_institution:        str       = Field(..., alias="origin_institution")
    academic_year:             str       = Field(..., alias="academic_year")
    current_gpa:               float     = Field(..., alias="current_gpa")
    desired_units_per_quarter: int       = Field(..., alias="desired_units_per_quarter")
    target_institution:        str       = Field(..., alias="target_institution")
    target_major:              str       = Field(..., alias="target_major")
    target_year:               str       = Field(..., alias="target_year")

@router.post("/schedule", response_model=Dict[str, Any])
async def schedule(req: ScheduleRequest):
    try:
        # Pass `desired_units_per_quarter` in as `unit_range` for scheduler
        result = sched.generate_schedule(
            completed_courses=req.completed_courses,
            target_major=req.target_major,
            target_institution=req.target_institution,
            academic_year=req.academic_year,
            unit_range=[req.desired_units_per_quarter, req.desired_units_per_quarter],
            preferred_times=None,              # or extract from req if you add it
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {e}")

    return result