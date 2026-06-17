FROM python:3.10-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code files
COPY backend/ /workspace/backend/
COPY ai_service/ /workspace/ai_service/

ENV PYTHONPATH=/workspace

EXPOSE 8000

CMD ["python", "backend/app/main.py"]
