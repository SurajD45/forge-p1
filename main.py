import sys
import json
from agents.explorer import run_explorer, force_intent_extraction
from utils.trd_builder import build_trd, generate_trd_markdown
from utils.schema_validator import validate_trd

# Hard cap: 2 question rounds max. Enforced by code, not LLM.
MAX_ROUNDS = 2

AUTH_SIGNALS = ["user", "account", "login", "profile", "member", "role", "permission"]


def apply_deterministic_corrections(intent: dict) -> dict:
    """Deterministic post-processing. Catches auth signals LLM may miss."""
    features_str = " ".join(intent.get("features", [])).lower()
    if any(signal in features_str for signal in AUTH_SIGNALS):
        intent["needs_auth"] = True
    return intent


def display_questions(content: list):
    print("\n--- Project Discovery ---")
    for i, item in enumerate(content):
        if isinstance(item, dict):
            print(f"\n{i+1}. {item.get('question', item)}")
            for idx, opt in enumerate(item.get("options", [])):
                print(f"   [{idx+1}] {opt}")
        else:
            print(f"\n{i+1}. {item}")


def main():
    print("=== FORGE (P1) - Agentic Discovery Studio ===")
    user_prompt = input("Describe your backend project idea:\n> ").strip()

    if not user_prompt:
        print("\nNo input provided. Pipeline halted.")
        return

    history = [f"Initial Idea: {user_prompt}"]
    current_round = 0
    final_intent = None

    # Question rounds — capped at MAX_ROUNDS by code
    while current_round < MAX_ROUNDS:
        print(f"\n[Round {current_round + 1}/{MAX_ROUNDS}] Analysing requirements...")

        try:
            response = run_explorer(user_prompt, history)
        except Exception as e:
            print(f"\nCRITICAL FAILURE: Explorer Agent error: {e}")
            sys.exit(1)

        if response.get("type") == "error":
            print(f"\nPipeline halted: {response.get('message')}")
            sys.exit(1)

        # LLM has enough info — extract now
        if response.get("type") == "intent":
            final_intent = response
            break

        # LLM wants more info — show questions
        content = response.get("content", [])
        display_questions(content)

        user_answer = input("\nYour answer: ").strip()
        history.append(f"Questions: {content} | Answer: {user_answer}")
        current_round += 1

    # MAX_ROUNDS hit — force extraction from everything collected
    if final_intent is None:
        print(f"\n[Final Round] Extracting intent from collected answers...")
        try:
            final_intent = force_intent_extraction(user_prompt, history)
        except Exception as e:
            print(f"\nCRITICAL FAILURE: Force extraction failed: {e}")
            sys.exit(1)

    if final_intent.get("type") == "error":
        print(f"\nPipeline halted: {final_intent.get('message')}")
        sys.exit(1)

    # Deterministic corrections
    final_intent = apply_deterministic_corrections(final_intent)

    # Build and validate TRD
    trd = build_trd(final_intent)

    try:
        validate_trd(trd)
    except Exception as e:
        print(f"\nTRD Validation Error: {e}")
        sys.exit(1)

    # Generate artifacts
    generate_trd_markdown(trd)

    print("\n--- Output ---")
    print(f"  Project  : {trd['project_name']}")
    print(f"  Stack    : {trd['stack']}")
    print(f"  Database : {trd['database']}")
    print(f"  Auth     : {trd['auth']}")
    print(f"  Features : {', '.join(trd['features'])}")
    print("\nTRD.json and TRD.md generated successfully.")
    print("Pipeline ready for Architect Phase.")


if __name__ == "__main__":
    main()