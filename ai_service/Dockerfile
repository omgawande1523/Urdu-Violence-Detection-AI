FROM python:3.10-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list
COPY ai_service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code files
COPY ai_service/ /workspace/ai_service/

ENV PYTHONPATH=/workspace

EXPOSE 8001

CMD ["uvicorn", "ai_service.app.service:app", "--host", "0.0.0.0", "--port", "8001"]
