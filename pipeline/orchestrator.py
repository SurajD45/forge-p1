import sys
from agents.explorer import run_explorer, force_intent_extraction
from agents.architect import run_architect
from utils.trd_builder import build_trd, generate_trd_markdown
from utils.arch_builder import build_arch, generate_arch_markdown
from utils.schema_validator import validate_trd, validate_arch
from utils.file_utils import read_json, write_json

MAX_ROUNDS = 2
AUTH_SIGNALS = ["user", "account", "login", "profile", "member", "role", "permission"]


def apply_deterministic_corrections(intent: dict) -> dict:
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


def stage_explorer():
    print("\n========================================")
    print(" STAGE 1: Explorer Agent")
    print("========================================")

    user_prompt = input("\nDescribe your backend project idea:\n> ").strip()
    if not user_prompt:
        print("\nNo input provided. Pipeline halted.")
        sys.exit(1)

    history = [f"Initial Idea: {user_prompt}"]
    current_round = 0
    final_intent = None

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

        if response.get("type") == "intent":
            final_intent = response
            break

        content = response.get("content", [])
        display_questions(content)
        user_answer = input("\nYour answer: ").strip()
        history.append(f"Questions: {content} | Answer: {user_answer}")
        current_round += 1

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

    final_intent = apply_deterministic_corrections(final_intent)
    trd = build_trd(final_intent)

    try:
        validate_trd(trd)
    except Exception as e:
        print(f"\nTRD Validation Error: {e}")
        sys.exit(1)

    generate_trd_markdown(trd)

    print("\n[Stage 1 Complete]")
    print(f"  Project  : {trd['project_name']}")
    print(f"  Stack    : {trd['stack']}")
    print(f"  Database : {trd['database']}")
    print(f"  Auth     : {trd['auth']}")
    print(f"  Features : {', '.join(trd['features'])}")
    print("  TRD.json and TRD.md written to output/")

    return trd


def stage_architect(trd: dict):
    print("\n========================================")
    print(" STAGE 2: Architect Agent")
    print("========================================")
    print("\nGenerating architecture from TRD...")

    try:
        arch_raw = run_architect(trd)
    except Exception as e:
        print(f"\nCRITICAL FAILURE: Architect Agent error: {e}")
        sys.exit(1)

    if arch_raw.get("type") == "error":
        print(f"\nPipeline halted: {arch_raw.get('message')}")
        sys.exit(1)

    arch = build_arch(arch_raw, trd)

    try:
        validate_arch(arch)
    except Exception as e:
        print(f"\nARCH Validation Error: {e}")
        sys.exit(1)

    generate_arch_markdown(arch)

    print("\n[Stage 2 Complete]")
    print(f"  Files    : {', '.join(arch['file_list'])}")
    print(f"  Entry    : {arch['entry_file']}")
    print("  ARCH.json and ARCH.md written to output/")

    return arch


def run_pipeline():
    print("=== FORGE (P1) - Agentic Dev Studio ===")

    # Stage 1
    trd = stage_explorer()

    # Stage 2
    arch = stage_architect(trd)

    print("\n========================================")
    print(" Pipeline Complete")
    print("========================================")
    print("  output/TRD.json")
    print("  output/TRD.md")
    print("  output/ARCH.json")
    print("  output/ARCH.md")
    print("\nReady for Developer Agent phase.")