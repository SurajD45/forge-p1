# FORGE — P1 Agentic Dev Studio

> Autonomous multi-agent SDLC pipeline that converts a vague project idea into a validated, structured backend project.

---

## What This Project Is

FORGE is a multi-agent system built with CrewAI and Groq (Llama 3.3 70B). It replaces the chaotic "paste your idea into ChatGPT and get random code" workflow with a structured, deterministic pipeline.

**Core philosophy:**
- LLM handles reasoning (understanding natural language)
- Deterministic code handles control (making architecture decisions)
- These two responsibilities are never mixed

**What it does right now:**
1. Takes your backend project idea as input
2. Runs an iterative discovery interview (max 2 rounds of questions)
3. Extracts structured intent from your answers
4. Makes deterministic decisions (stack, database, auth)
5. Validates output against a strict JSON schema
6. Generates `TRD.json` and `TRD.md` — Technical Requirements Document
7. Automatically advances to Architect Agent
8. Generates `ARCH.json` and `ARCH.md` — Architecture Document with file structure, module responsibilities, and dependency order

**What it does NOT do yet:**
- Generate code (Developer Agent is planned next)
- Deploy anything
- Touch your existing codebase

---

## Current Agent Status

| Agent | Status | Responsibility |
|---|---|---|
| Explorer Agent | Complete | Discovery interview -> TRD.json + TRD.md |
| Architect Agent | Complete | TRD -> ARCH.json + ARCH.md |
| Developer Agent | Planned | ARCH -> code files with AST validation |
| Reviewer Agent | Planned | Cross-file consistency check |

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | CrewAI |
| LLM Provider | Groq (Llama 3.3 70B) |
| Language | Python 3.11 |
| Schema Validation | jsonschema |
| Environment | python-dotenv |
| Containerisation | Docker |

---

## Project Structure

```
forge-p1/
├── main.py                      # Entry point — 3 lines, calls orchestrator
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
│
├── .env.example                 # Copy this to .env and fill in your key
├── .gitignore
├── .dockerignore
│
├── pipeline/
│   ├── __init__.py
│   └── orchestrator.py          # Controls pipeline flow — Stage 1 then Stage 2
│
├── agents/
│   ├── __init__.py
│   ├── explorer.py              # Explorer Agent — iterative discovery + intent extraction
│   └── architect.py             # Architect Agent — file structure + module design
│
├── schemas/
│   ├── trd_schema.json          # Frozen TRD contract
│   └── arch_schema.json         # Frozen ARCH contract
│
├── utils/
│   ├── __init__.py
│   ├── trd_builder.py           # Deterministic TRD builder — no LLM
│   ├── arch_builder.py          # Deterministic ARCH builder — no LLM
│   ├── schema_validator.py      # Validates TRD and ARCH against schemas
│   └── file_utils.py            # Shared read/write helpers
│
└── output/                      # All generated artifacts appear here
    ├── TRD.json
    ├── TRD.md
    ├── ARCH.json
    └── ARCH.md
```

---

## Getting a Groq API Key

1. Go to https://console.groq.com
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy it — you will paste it into your `.env` file

---

## Option A: Run with Docker (Recommended)

Docker is recommended because it requires no Python setup on your machine.

### Prerequisites

- Docker Desktop installed and running: https://docs.docker.com/get-docker/
- A Groq API key (see above)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/SurajD45/forge-p1.git
cd forge-p1

# 2. Create your environment file
cp .env.example .env
```

Open `.env` and replace `your-groq-api-key-here` with your actual key:

```
GROQ_API_KEY=your-actual-key-here
CREWAI_DISABLE_TELEMETRY=true
OTEL_SDK_DISABLED=true
```

```bash
# 3. Build the Docker image (only needed once)
docker compose build

# 4. Run the studio
docker compose run forge
```

### What happens

- Terminal asks you to describe your backend project idea
- Explorer Agent runs 1-2 rounds of clarifying questions
- TRD.json and TRD.md are generated in `output/`
- Architect Agent runs automatically
- ARCH.json and ARCH.md are generated in `output/`

### Useful Docker commands

```bash
# Run the studio
docker compose run forge

# Rebuild after code changes
docker compose build

# Rebuild from scratch (use when requirements.txt changes)
docker compose build --no-cache

# See all built images
docker images

# Clean up orphan containers
docker compose run --remove-orphans forge
```

---

## Option B: Run Locally (Without Docker)

### Prerequisites

- Python 3.11+
- A Groq API key

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/SurajD45/forge-p1.git
cd forge-p1

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file
cp .env.example .env
# Open .env and add your GROQ_API_KEY

# 5. Run
python main.py
```

Generated files will appear in the `output/` folder.

---

## How the Pipeline Works (For Contributors)

Understanding this before writing code is mandatory.

### Pipeline Flow

```
python main.py
  └── orchestrator.run_pipeline()
        ├── Stage 1: Explorer Agent
        │     └── iterative discovery -> TRD.json + TRD.md
        ├── Gate: TRD.json exists? No -> halt
        ├── Stage 2: Architect Agent
        │     └── file structure design -> ARCH.json + ARCH.md
        └── Gate: ARCH.json exists? No -> halt (Developer Agent goes here)
```

### Decision Rules (Deterministic — never change without discussion)

| Signal from user | Decision made by system |
|---|---|
| scale == "high" | database = postgresql |
| scale == "low" (default) | database = sqlite |
| needs_auth == true | auth = jwt |
| needs_auth == false (default) | auth = none |
| Auth keywords found in features | needs_auth forced to true |
| auth == "jwt" | auth.py injected into file_list |
| database == "postgresql" | alembic.ini added |

### Supported Stack (V1 — locked)

- Framework: FastAPI only
- Database: SQLite or PostgreSQL
- Auth: JWT or none
- Project type: API only

Anything outside this list causes the pipeline to halt. This is intentional.

### Failure Behavior

This system fails loudly, never silently:
- Invalid JSON from LLM -> immediate halt, raw output shown
- Schema validation failure -> pipeline halts, artifact not written
- Missing intent fields -> warning printed, safe defaults applied
- MAX_ROUNDS hit -> force extraction from collected answers

---

## Contributing — Read This Before Writing Any Code

### Rules

1. **Never push directly to `main`**. All work goes through Pull Requests.
2. **One feature per branch**. Keep branches focused.
3. **Test your agent in isolation** before wiring it to the pipeline.
4. **Do not start the next agent** until the current one passes 3 end-to-end test cases.

### Branching

```bash
# Always start from latest main
git checkout main
git pull origin main

# Create your branch
git checkout -b feat/developer-agent
```

### Branch naming convention

| Type | Format | Example |
|---|---|---|
| New agent | `feat/agent-name` | `feat/developer-agent` |
| Bug fix | `fix/description` | `fix/trd-output-path` |
| Refactor | `refactor/description` | `refactor/explorer-prompt` |
| Documentation | `docs/description` | `docs/update-readme` |

### Workflow

```bash
# 1. Make your changes on your branch
# 2. Test with Docker
docker compose build
docker compose run forge

# 3. Commit
git add .
git commit -m "feat: add Developer Agent with AST validation"

# 4. Push your branch
git push origin feat/developer-agent

# 5. Open a Pull Request on GitHub into main
# 6. Wait for review before merging
```

---

## What to Build Next — Developer Agent

The Developer Agent is the next milestone. It takes `ARCH.json` + `TRD.json` as input and generates all project files.

**Input contract (what you receive):**
```json
{
  "project_name": "string",
  "file_list": ["main.py", "database.py", "models.py", "routes.py"],
  "module_responsibilities": {
    "main.py": "FastAPI app entry point",
    "database.py": "Database connection and session management"
  },
  "dependency_order": ["database.py", "models.py", "routes.py", "main.py"],
  "entry_file": "main.py",
  "app_object": "app",
  "framework": "fastapi",
  "database": "sqlite or postgresql",
  "auth": "jwt or none"
}
```

**Output contract (what you must produce):**
- One `.py` file per entry in `file_list`
- Each file AST-validated before being written to disk
- Files generated in `dependency_order` — least dependent first
- Full TRD + ARCH context injected into every LLM call
- If AST validation fails: retry up to 2 times, then halt loudly

**Rules:**
- LLM generates file content
- AST validation is deterministic — `ast.parse()` on every file before write
- Full context re-injected every call (no context drift)
- Create your branch: `git checkout -b feat/developer-agent`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key from console.groq.com |
| `CREWAI_DISABLE_TELEMETRY` | Yes | Set to `true` — disables CrewAI tracing prompts |
| `OTEL_SDK_DISABLED` | Yes | Set to `true` — disables OpenTelemetry |

---

## Important Rules

- `.env` is never committed. Never share your API key.
- `output/` files are generated artifacts. They are in `.gitignore`. Do not commit them.
- The `output/` folder exists via `output/.gitkeep`. Do not delete `.gitkeep`.