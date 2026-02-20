# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]