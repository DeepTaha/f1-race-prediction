# ==============================================================================
# F1 Prediction System - Production Dockerfile
# ==============================================================================

FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# System deps for numpy/sklearn compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cached layer unless requirements change)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY artifacts/ ./artifacts/
COPY dataset/ ./dataset/

# Non-root user for security
RUN useradd -m -u 1000 f1user && chown -R f1user:f1user /app
USER f1user

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
