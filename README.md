# FORGE — P1 Agentic Dev Studio

> Autonomous multi-agent SDLC pipeline that converts a vague project idea into a validated Technical Requirements Document (TRD).

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
6. Generates `TRD.json` and `TRD.md` in the `output/` folder

**What it does NOT do yet:**
- Generate code (Architect and Developer agents are planned)
- Deploy anything
- Touch your existing codebase

---

## Current Agent Status

| Agent | Status | Responsibility |
|---|---|---|
| Explorer Agent | Complete | Discovery interview -> TRD.json + TRD.md |
| Architect Agent | Planned | TRD -> ARCH.json + file structure |
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

---

## Project Structure

```
forge-p1/
├── main.py                  # Entry point — runs the discovery pipeline
├── Dockerfile               # Container definition
├── docker-compose.yml       # Run configuration
├── requirements.txt         # Python dependencies
├── README.md
│
├── .env.example             # Copy this to .env and fill in your key
├── .gitignore               # .env and output files are never committed
├── .dockerignore
│
├── agents/
│   └── explorer.py          # Explorer Agent — iterative discovery + intent extraction
│
├── schemas/
│   └── trd_schema.json      # Frozen TRD contract — validation failure halts pipeline
│
├── utils/
│   ├── trd_builder.py       # Deterministic TRD builder — no LLM involved
│   └── schema_validator.py  # jsonschema validator
│
└── output/                  # Generated artifacts appear here
    ├── TRD.json             # Machine-readable requirements document
    └── TRD.md               # Human-readable requirements document
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
git clone https://github.com/YOUR_USERNAME/forge-p1.git
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
docker build -t forge-p1 .

# 4. Run the studio
docker compose run forge
```

### What happens next

- The terminal will ask you to describe your backend project idea
- It will ask 1-2 rounds of clarifying questions
- After you answer, it generates your TRD
- `TRD.json` and `TRD.md` will appear in the `output/` folder on your machine

### Useful Docker commands

```bash
# Run the studio
docker compose run forge

# Rebuild after code changes
docker compose build

# See all built images
docker images

# Remove the image and start fresh
docker rmi forge-p1
```

---

## Option B: Run Locally (Without Docker)

### Prerequisites

- Python 3.11+
- A Groq API key

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/forge-p1.git
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

### Decision Rules (Deterministic — never change without discussion)

| Signal from user | Decision made by system |
|---|---|
| scale == "high" | database = postgresql |
| scale == "low" (default) | database = sqlite |
| needs_auth == true | auth = jwt |
| needs_auth == false (default) | auth = none |
| Auth keywords found in features | needs_auth forced to true |

### Supported Stack (V1 — locked)

- Framework: FastAPI only
- Database: SQLite or PostgreSQL
- Auth: JWT or none
- Project type: API only

Anything outside this list causes the pipeline to halt. This is intentional.

### Failure Behavior

This system fails loudly, never silently:
- Invalid JSON from LLM -> immediate halt, raw output shown
- Schema validation failure -> pipeline halts, TRD.json not written
- Missing intent fields -> warning printed, safe defaults applied

---

## Contributing — Read This Before Writing Any Code

### Rules

1. **Never push directly to `main`**. Main is protected. All work goes through Pull Requests.
2. **One feature per branch**. Keep branches focused.
3. **Test your agent in isolation** before wiring it to the pipeline.

### Branching

```bash
# Always start from latest main
git checkout main
git pull origin main

# Create your branch
git checkout -b feat/architect-agent
```

### Branch naming convention

| Type | Format | Example |
|---|---|---|
| New agent | `feat/agent-name` | `feat/architect-agent` |
| Bug fix | `fix/description` | `fix/trd-output-path` |
| Refactor | `refactor/description` | `refactor/explorer-prompt` |
| Documentation | `docs/description` | `docs/update-readme` |

### Workflow

```bash
# 1. Make your changes
# 2. Test locally
python main.py

# 3. Commit with a clear message
git add .
git commit -m "feat: add Architect Agent with ARCH.json output"

# 4. Push your branch
git push origin feat/architect-agent

# 5. Open a Pull Request on GitHub into main
# 6. Wait for review before merging
```

---

## What to Build Next — Architect Agent

The next milestone is the Architect Agent. It takes `TRD.json` as input and produces:
- `ARCH.json` — machine-readable file structure, module responsibilities, dependency order
- `ARCH.md` — human-readable architecture document

**Input contract (what you receive from Explorer):**
```json
{
  "project_name": "string",
  "project_type": "api",
  "stack": "fastapi",
  "database": "sqlite or postgresql",
  "auth": "jwt or none",
  "features": ["list of features"],
  "constraints": [],
  "out_of_scope": []
}
```

**Output contract (what you must produce):**
```json
{
  "project_name": "string",
  "file_list": ["main.py", "models.py", "routes.py", "database.py"],
  "module_responsibilities": {
    "main.py": "FastAPI app entry point",
    "models.py": "SQLAlchemy ORM models",
    "routes.py": "API route handlers",
    "database.py": "Database connection and session"
  },
  "dependency_order": ["database.py", "models.py", "routes.py", "main.py"],
  "entry_file": "main.py",
  "app_object": "app",
  "framework": "fastapi"
}
```

**Rules for building it:**
- LLM generates the file list and module responsibilities
- Deterministic code validates the output schema
- Pipeline halts on invalid output
- Do not start Developer Agent until Architect passes 3 end-to-end test cases
- Create your branch: `git checkout -b feat/architect-agent`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key from console.groq.com |
| `CREWAI_DISABLE_TELEMETRY` | Yes | Set to `true` — disables CrewAI tracing prompts |
| `OTEL_SDK_DISABLED` | Yes | Set to `true` — disables OpenTelemetry |

---

## Important Rules

- `.env` is never committed. It is in `.gitignore`. Never share your API key.
- `output/TRD.json` and `output/TRD.md` are generated files. They are in `.gitignore`. Do not commit them.
- The `output/` folder exists in the repo via `output/.gitkeep`. Do not delete `.gitkeep`.