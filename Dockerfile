FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY agents/ ./agents/
COPY utils/ ./utils/
COPY schemas/ ./schemas/
COPY main.py .

# Output directory for generated artifacts
RUN mkdir -p /app/output

# Run interactively
CMD ["python", "main.py"]