import os
import json
import re
from crewai import Agent, Task, Crew, LLM


def _call_llm(description: str, expected: str) -> dict:
    """Single reusable LLM call. Returns parsed JSON dict or error dict."""
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
    agent = Agent(
        role="Technical Discovery Specialist",
        goal="Extract structured project intent or ask targeted discovery questions.",
        backstory="You are a senior backend architect. You output only raw JSON. No prose.",
        llm=llm,
        verbose=False
    )
    task = Task(description=description, expected_output=expected, agent=agent)
    result = Crew(agents=[agent], tasks=[task], verbose=False).kickoff()
    raw = str(result).strip()

    match = re.search(r'(\{.*\})', raw, re.DOTALL)
    if not match:
        print(f"\nFORGE FAIL: No JSON found in LLM output.")
        print(f"RAW: {raw}")
        return {"type": "error", "message": "No JSON in response"}

    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        print(f"\nFORGE FAIL: JSON decode error.")
        print(f"RAW: {raw}")
        return {"type": "error", "message": "JSON decode failed"}


def run_explorer(user_prompt: str, history: list = None) -> dict:
    """
    Returns type 'questions' with content list, or type 'intent' with
    all required TRD fields at the top level.
    """
    conversation = "\n".join(history) if history else "Initial prompt only."

    description = f"""
User Prompt: {user_prompt}
Conversation History: {conversation}

DECISION RULE:
- If you need more information -> return type "questions"
- If you have enough information -> return type "intent"

QUESTIONS FORMAT (use when more info needed):
{{
  "type": "questions",
  "content": [
    {{
      "question": "Short targeted question",
      "options": ["Option A", "Option B", "Option C"]
    }}
  ]
}}

INTENT FORMAT (use when ready to extract):
{{
  "type": "intent",
  "project_name": "lowercase-hyphenated-name",
  "features": ["feature 1", "feature 2", "feature 3"],
  "scale": "low or high",
  "needs_auth": true or false,
  "constraints": [],
  "out_of_scope": []
}}

STRICT RULES:
- Intent field names must be EXACTLY: project_name, features, scale, needs_auth, constraints, out_of_scope
- scale is "high" ONLY if thousands of users or high concurrency is mentioned. Default: "low"
- needs_auth is true ONLY if login, user accounts, or auth is mentioned. Default: false
- features must be functional capabilities only. No infrastructure. No scale concerns.
- Do NOT ask about programming language or framework. The system uses FastAPI. Not negotiable.
- Return raw JSON only. No markdown. No code fences. No explanation.
"""

    parsed = _call_llm(
        description,
        "Raw JSON with type 'questions' or 'intent'. No markdown. No prose."
    )

    if parsed.get("type") == "intent":
        parsed = _validate_intent_fields(parsed)

    return parsed


def force_intent_extraction(user_prompt: str, history: list) -> dict:
    """
    Called when MAX_ROUNDS is hit. Forces the LLM to return intent
    using everything collected in conversation history.
    """
    conversation = "\n".join(history) if history else "Initial prompt only."

    description = f"""
User Prompt: {user_prompt}
Conversation History (all answers collected): {conversation}

INSTRUCTION: You MUST return type "intent" now. Do not ask more questions.
Use all information from the conversation history.
Make reasonable assumptions for anything still unclear.

Return this exact structure:
{{
  "type": "intent",
  "project_name": "lowercase-hyphenated-name",
  "features": ["feature 1", "feature 2", "feature 3"],
  "scale": "low or high",
  "needs_auth": true or false,
  "constraints": [],
  "out_of_scope": []
}}

RULES:
- project_name: derive from the project idea. Lowercase, hyphenated.
- features: list every functional capability mentioned in the conversation.
- scale: "high" if thousands of users mentioned, otherwise "low".
- needs_auth: true if login, accounts, or auth mentioned, otherwise false.
- Return raw JSON only. No markdown. No code fences. No explanation.
"""

    parsed = _call_llm(
        description,
        "Raw JSON with type 'intent' and all required fields populated."
    )

    return _validate_intent_fields(parsed)


def _validate_intent_fields(parsed: dict) -> dict:
    """Ensure all required intent fields exist. Fill missing with safe defaults."""
    defaults = {
        "project_name": "unnamed-project",
        "features": [],
        "scale": "low",
        "needs_auth": False,
        "constraints": [],
        "out_of_scope": []
    }
    for field, default in defaults.items():
        if field not in parsed:
            print(f"  [WARN] Intent missing field '{field}'. Using default: {default}")
            parsed[field] = default

    parsed["type"] = "intent"
    return parsed