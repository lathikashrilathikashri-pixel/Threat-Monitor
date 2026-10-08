# ===================================================================================
# Multi-stage Dockerfile for Cloud Production Backend (Render, Railway, Fly.io, AWS)
# ===================================================================================

FROM python:3.11-slim

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Install system dependencies for psycopg2 and network tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Run as non-root security analyst user
RUN useradd -m socuser && chown -R socuser:socuser /app
USER socuser

EXPOSE 5000

# Start production WSGI server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "app:app"]
