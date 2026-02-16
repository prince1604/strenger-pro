FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (PostgreSQL only, no MySQL)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip for better reliability
RUN pip install --upgrade pip

# Copy and install Python dependencies with retry
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 5 --timeout 100 -r requirements.txt

# Copy application code
COPY . .

# Run the application
CMD ["gunicorn", "-w", "1", "--threads", "4", "--timeout", "120", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
