FROM python:3.11-slim-bookworm

WORKDIR /app

# Speed up pip and Python
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps needed for FAISS, lxml, pandas, PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libblas-dev \
    liblapack-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first for faster wheel resolution
RUN pip install --upgrade pip setuptools wheel

# Copy only requirements first to cache this layer
COPY requirements.txt .

# Huge speed-up: prefer prebuilt wheels when possible
RUN pip install --prefer-binary -r requirements.txt

# Copy main application
COPY . .

# Create necessary folders
RUN mkdir -p /app/database /app/data /app/index

# Optional: pre-download transformer model (saves startup time)
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
