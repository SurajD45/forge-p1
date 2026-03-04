# FORGE — P1 Agentic Dev Studio

Autonomous multi-agent SDLC pipeline. Takes a project idea, runs structured discovery, and generates a Technical Requirements Document (TRD).

## Current Status
- Explorer Agent: Complete
- Architect Agent: Planned
- Developer Agent: Planned
- Reviewer Agent: Planned

---

## Option A: Run with Docker (Recommended)

### Prerequisites
- Docker installed: https://docs.docker.com/get-docker/

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/forge-p1.git
cd forge-p1

# 2. Set up your environment
cp .env.example .env
# Open .env and add your GROQ_API_KEY

# 3. Build and run
docker compose run forge
```

Generated TRD.json and TRD.md will appear in the `output/` folder on your machine.

---

## Option B: Run locally (without Docker)

### Prerequisites
- Python 3.11+

### Steps

```bash
# 1. Clone and enter the repo
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

# 4. Set up environment
cp .env.example .env
# Open .env and add your GROQ_API_KEY

# 5. Run
python main.py
```

---

## Getting a Groq API Key
1. Go to https://console.groq.com
2. Sign up / log in
3. Create an API key
4. Paste it into your `.env` file

## Contributing
- Never push to `main` directly
- Create a branch: `git checkout -b feat/your-feature-name`
- Open a Pull Request into `main`