AutoClass Agent

AutoClass Agent is an AI-powered academic scheduling assistant designed for community college students planning to transfer. It generates optimized, quarter-by-quarter schedules tailored to your completed coursework, target university and major, desired course load, and GPA.

📦 Features

- Input:
  - Completed courses
  - Origin college
  - Current GPA
  - Target university and major
  - Desired units per quarter
  - Preferred starting quarter

- Output:
  - Quarter-by-quarter transfer schedule
  - Pre-requisite sequencing
  - Balanced workload based on GPA
  - JSON or visual table output

- Powered by:
  - Perplexity Sonar Pro API
  - FastAPI backend and Next.js frontend
  - Clean card-style UI with Tailwind CSS

🧪 Tech Stack

| Layer       | Tech                                   |
|-------------|----------------------------------------|
| Frontend    | Next.js 14, Tailwind CSS               |
| State Mgmt  | Zustand, React Hook Form               |
| Backend     | FastAPI (Python 3.12)                  |
| AI Engine   | Perplexity Labs - Sonar Pro            |
| Hosting     | Local development via localhost        |

🚀 Getting Started
1. Clone the repo

git clone https://github.com/your-username/autoclass-agent.git
cd autoclass-agent

2. Frontend Setup

cd frontend
npm install
npm run dev

Access at: http://localhost:3000

3. Backend Setup

cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Create a .env file in backend/ with:
SONAR_API_KEY=your-perplexity-api-key
PORT=8000

Run the backend:
uvicorn app.main:app --reload

Access at: http://localhost:8000

📤 API Overview
POST /sonar/schedule
Request body:

{
  "completed_courses": ["MATH 1A", "MATH 1B"],
  "origin_institution": "De Anza College",
  "academic_year": "2025",
  "target_institution": "UC Berkeley",
  "target_major": "Applied Math",
  "desired_units_per_quarter": "12",
  "current_gpa": "3.7"
}

Response body:

{
  "schedule": [
    {
      "term": "Fall 2025",
      "courses": [
        {
          "code": "MATH 2",
          "title": "Multivariable Calculus",
          "units": 4
        }
      ]
    }
  ],
  "warnings": [],
  "citations": [],
  "reminder_to_meet_counselor": false
}

🧠 Prompt Logic

The system prompt sent to Sonar includes:
- Major & institution articulation requirements
- Pre-requisite enforcement
- Unit load cap (from user)
- GPA-based difficulty balancing
- Preferred quarter starting point
- Response format enforced as pure JSON

📌 Roadmap

- Real-time Assist.org integration
- Add transfer planner export (PDF/CSV)
- Add multi-quarter GPA trends
- Auto-detect completed GE areas

👤 Author

- Charles Lee (charleslee@autoclass.ai)
- Project part of AI Agent Club, De Anza College

📄 License

This project is released under The Unlicense:

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

For more information, please refer to http://unlicense.org/

