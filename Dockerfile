# -------------------------
# Base image
# -------------------------
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure stdout/stderr are unbuffered
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# -------------------------
# System dependencies
# -------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------
# Install Python dependencies
# -------------------------
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# -------------------------
# Copy application code
# -------------------------
COPY . .

# -------------------------
# Create non-root user (security best practice)
# -------------------------
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

USER appuser

# -------------------------
# Expose port
# -------------------------
EXPOSE 8000

# -------------------------
# Run application
# -------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]