# backend/app/modules/sonar_client.py

import requests
import json
from typing import Any, Dict, List, Optional
from app.config import settings

class SonarClient:
    """
    Queries Perplexity’s Sonar API via chat/completions.
    Ensures the response is parsed into a Python dict,
    handling cases where JSON is returned as a string, and logs raw output for debugging.
    """

    BASE_URL = "https://api.perplexity.ai/chat/completions"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.SONAR_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def query(self, user_query: str, timeout: int = 30) -> Dict[str, Any]:
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a JSON-only course scheduler. "
                        "Always respond *only* with the exact JSON—no extraneous text. "
                        "Example response format:\n"
                        "```\n"
                        "{\n"
                        "  \"quarters\": [\n"
                        "    { \"term\": \"Fall 2025\", \"courses\": [\n"
                        "        {\"code\": \"MATH 1A\", \"title\": \"Calculus I\", \"units\": 4}\n"
                        "      ]\n"
                        "    }\n"
                        "  ],\n"
                        "  \"warnings\": [\n"
                        "    {\"term\": \"Fall 2025\", \"code\": \"COMPSCI 61C\", \"message\": \"No articulation—see counselor.\"}\n"
                        "  ],\n"
                        "  \"reminder_to_meet_counselor\": false\n"
                        "}\n"
                        "```"
                    )
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ]
        }

        resp = requests.post(
            self.BASE_URL,
            headers=self.headers,
            json=payload,
            timeout=timeout
        )
        resp.raise_for_status()

        body = resp.json()
        raw = body["choices"][0]["message"]["content"]

        print("\n🛰️ Sonar raw output:\n", raw, "\n")

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to JSON-decode Sonar response:\n{raw}")

        if isinstance(parsed, str):
            try:
                parsed = json.loads(parsed)
            except json.JSONDecodeError:
                raise ValueError(f"Failed second-pass decode of Sonar response:\n{parsed}")

        if not isinstance(parsed, dict):
            raise ValueError(f"Unexpected Sonar response type: {type(parsed)}, content:\n{parsed}")

        return parsed

    def build_prompt(
        self,
        completed_courses: List[str],
        target_major: str,
        target_institution: str,
        academic_year: str,
        unit_range: Optional[List[int]] = None,
        preferred_times: Optional[List[str]] = None
    ) -> str:
        """
        1) On ASSIST.org, select the student's ORIGIN institution and the DESTINATION institution+major.
           Pull the full list of articulated major courses.
        2) Remove courses already completed.
        3) For each remaining course:
             a) Check prerequisites; if unmet, queue that prerequisite first.
             b) Go to the ORIGIN institution’s official course catalog or website:
                - Verify the course is offered in the term `academic_year`.
                - Record its official unit value.
        4) Build a schedule up to `unit_range`, alternating major vs. GE/elective based on GPA:
             - GPA < 3.0: alternate major and elective.
             - GPA ≥ 3.0: up to two majors before an elective.
        5) Return **only** a JSON object—no extra text, using the schema:
           {
             "quarters":[{"term":"…","courses":[{"code":"…","title":"…","units":4}]}],
             "warnings":[],
             "reminder_to_meet_counselor":false
           }
        """
        steps: List[str] = [
            # 1: ASSIST lookup
            (
                f"Step 1: On ASSIST.org, select the origin institution and "
                f"the target institution '{target_institution}' + major '{target_major}'. "
                "List all articulated courses for that major."
            ),

            # 2: filter completed
            (
                "Step 2: Remove any courses the student has already completed: "
                + (", ".join(completed_courses) if completed_courses else "none")
            ),

            # 3: verify via origin catalog
            (
                "Step 3: For each remaining course, check prerequisites—"
                "if unmet, schedule those prerequisites first. Then visit the ORIGIN institution’s "
                f"official course catalog or website to confirm each course is offered in '{academic_year}' "
                "and to record its exact unit value."
            ),

            # 4: scheduling logic
            (
                "Step 4: Build the quarter schedule to fill between "
                f"{unit_range[0]} and {unit_range[1]} units. "
                "Alternate major courses with GE/elective courses if GPA is below 3.0; "
                "otherwise schedule up to two major courses consecutively before an elective."
            ),
        ]

        if preferred_times:
            steps.append(
                "Step 4b: Prefer course times in " + ", ".join(preferred_times) + "."
            )

        steps.append(
            "Step 5: Respond **only** with the JSON object—no extra text or markdown."
            " Use the exact structure shown above."
        )

        return "\n\n".join(steps)