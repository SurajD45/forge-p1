

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/
COPY pipeline/ ./pipeline/
COPY utils/ ./utils/
COPY schemas/ ./schemas/
COPY main.py .

RUN mkdir -p /app/output

CMD ["python", "main.py"]