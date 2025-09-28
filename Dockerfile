# ------------ Base Python Image ------------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

# System deps (tesseract + fonts + build tools for opencv/pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY . .

# Expose application port (gunicorn uses 8000)
EXPOSE 8000

# Environment defaults (override in runtime env / container orchestrator)
ENV FLASK_ENV=production \
    FLASK_DEBUG=False \
    OPENAI_BASE_URL= \
    OPENAI_API_KEY= \
    LLM_MODEL_NAME=llama-3.3-70b-instruct \
    SAVE_RESULTS=True

# Health check script (simple)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import requests,os;import sys;\n\nimport json;\nurl='http://localhost:8000/api/health';\n\nimport urllib.request, json;\ntry:\n  r=urllib.request.urlopen(url,timeout=4);\n  import sys; sys.exit(0 if r.status==200 else 1)\nexcept Exception as e: sys.exit(1)" || exit 1

# Run with gunicorn
CMD ["gunicorn", "wsgi:app", "-c", "gunicorn.conf.py"]
