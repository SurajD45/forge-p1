import os
import json
import re
from crewai import Agent, Task, Crew, LLM


def _call_llm(description: str, expected: str) -> dict:
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
    agent = Agent(
        role="Senior Backend Architect",
        goal="Design a clean, minimal file structure for a FastAPI backend project.",
        backstory="You are a senior backend architect. You output only raw JSON. No prose.",
        llm=llm,
        verbose=False
    )
    task = Task(description=description, expected_output=expected, agent=agent)
    result = Crew(agents=[agent], tasks=[task], verbose=False).kickoff()
    raw = str(result).strip()

    match = re.search(r'(\{.*\})', raw, re.DOTALL)
    if not match:
        print(f"\nFORGE FAIL: No JSON found in Architect output.")
        print(f"RAW: {raw}")
        return {"type": "error", "message": "No JSON in response"}

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        print(f"\nFORGE FAIL: JSON decode error in Architect output.")
        print(f"RAW: {raw}")
        return {"type": "error", "message": "JSON decode failed"}


def run_architect(trd: dict) -> dict:
    """
    Takes TRD dict. Returns raw architecture dict.
    LLM decides file structure and module responsibilities.
    Deterministic layer (arch_builder) injects mandatory files after.
    """
    description = f"""
You are designing the file structure for this FastAPI backend project.

TRD Input:
{json.dumps(trd, indent=2)}

Your job: design a minimal, production-quality file structure.

Return this exact JSON structure:
{{
  "project_name": "{trd['project_name']}",
  "file_list": ["main.py", "database.py", "models.py", "routes.py"],
  "module_responsibilities": {{
    "main.py": "FastAPI app entry point, mounts all routers",
    "database.py": "Database connection and session management",
    "models.py": "SQLAlchemy ORM models",
    "routes.py": "API route handlers"
  }},
  "dependency_order": ["database.py", "models.py", "routes.py", "main.py"],
  "entry_file": "main.py",
  "app_object": "app",
  "framework": "fastapi"
}}

STRICT RULES:
- framework must always be "fastapi"
- entry_file must always be "main.py"
- app_object must always be "app"
- file_list must include main.py, database.py, models.py
- dependency_order must list files from least dependent to most dependent
- module_responsibilities must have one entry per file in file_list
- Keep file structure minimal — no unnecessary files
- If auth is "jwt" in TRD, include auth.py in file_list
- If features mention payments, include payments.py
- Group related routes into separate route files (e.g. user_routes.py, booking_routes.py)
- Return raw JSON only. No markdown. No code fences. No explanation.
"""

    return _call_llm(
        description,
        "Raw JSON with file_list, module_responsibilities, dependency_order, entry_file, app_object, framework."
    )