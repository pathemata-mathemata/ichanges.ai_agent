from fastapi import APIRouter, Query
from typing import Dict, Any, List

from app.modules.assist_scraper import get_transfer_courses

router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.get("/requirements")
async def get_transfer_requirements(
    source_institution: str = Query(..., description="Source institution (where student is transferring from)"),
    target_institution: str = Query(..., description="Target institution (where student wants to transfer to)"),
    major: str = Query(..., description="Major/program of study"),
    completed_courses: List[str] = Query(None, description="List of course codes the student has already completed"),
    target_quarter: str = Query(None, description="Target quarter/term for transfer (e.g., 'Fall 2024')")
) -> Dict[str, Any]:
    """
    Get transfer course requirements from source to target institution for a specific major.
    Will check which courses have been completed by the student and mark remaining ones.
    """
    result = get_transfer_courses(
        source_institution=source_institution,
        target_institution=target_institution,
        major=major,
        completed_courses=completed_courses,
        target_quarter=target_quarter
    )
    
    return result 