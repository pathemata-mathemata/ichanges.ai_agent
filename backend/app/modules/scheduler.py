# backend/app/modules/scheduler.py

from typing import List, Optional, Dict, Any
from app.modules.sonar_client import SonarClient

class Scheduler:
    """
    Stateless scheduler that builds a Sonar prompt
    and returns schedule, warnings, and a counselor reminder flag.
    """

    def __init__(self):
        self.sonar = SonarClient()

    def generate_schedule(
        self,
        completed_courses: List[str],
        target_major: str,
        target_institution: str,
        academic_year: str,
        unit_range: Optional[List[int]] = None,
        preferred_times: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        # 1. Build the free-form prompt string
        prompt = self.sonar.build_prompt(
            completed_courses,
            target_major,
            target_institution,
            academic_year,
            unit_range,
            preferred_times
        )

        # 1a. Add scheduling guidelines for prerequisites, subject distribution, course prioritization, and transfer timing
        guidelines = (
            "Please ensure that course prerequisites are respected (e.g., schedule Math 1A before Math 1B), "
            "avoid scheduling more than one course from the same subject area in a single quarter, "
            "prioritize major-required courses before general education (GE) courses, "
            "and plan courses across upcoming quarters to complete all major requirements before the UC application period opens and finish all required coursework prior to transfer."
        )
        prompt = f"{prompt}\n\n{guidelines}"

        # 2. Query Sonar; it returns a dict already parsed from JSON
        try:
            result = self.sonar.query(user_query=prompt, timeout=30)
        except Exception:
            # Let FastAPI handler catch and convert to HTTP error
            raise

        warnings: List[Dict[str, Any]] = []
        schedule: List[Dict[str, Any]] = []
        reminder_to_meet = False

        # 3. Process each quarter returned
        for q in result.get("quarters", []):
            term = q.get("term")
            courses_out = []
            for c in q.get("courses", []):
                code = c.get("code")
                units = c.get("units")
                title = c.get("title")

                if c.get("no_articulation"):
                    reminder_to_meet = True
                    warnings.append({
                        "term": term,
                        "code": code,
                        "message": "No articulation found—please meet your ISP counselor."
                    })
                    continue

                if c.get("must_take_at_university"):
                    reminder_to_meet = True
                    warnings.append({
                        "term": term,
                        "code": code,
                        "message": "This course must be taken after transfer—please consult counselor."
                    })
                    # insert an elective placeholder
                    courses_out.append({
                        "code": "ELECTIVE",
                        "title": "Advisor-chosen elective",
                        "units": units or 3
                    })
                    continue

                # normal articulated course
                courses_out.append({
                    "code": code,
                    "title": title,
                    "units": units
                })

            schedule.append({"term": term, "courses": courses_out})

        return {
            "schedule": schedule,
            "warnings": warnings,
            "citations": result.get("citations", []),
            "reminder_to_meet_counselor": reminder_to_meet
        }
