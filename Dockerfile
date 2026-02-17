FROM python:3.11-slim

# Create a non-root user to run the app (Required for Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory to the user's home (where they have write permission)
WORKDIR $HOME/app

# Copy dependencies first for caching
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --retries 5 --timeout 100 -r requirements.txt

# Copy application code with correct ownership
COPY --chown=user . .

# Expose the port (Hugging Face expects 7860 by default)
EXPOSE 7860

# Run with Gunicorn on port 7860 (Hugging Face default) or $PORT if provided
CMD ["sh", "-c", "gunicorn -w 1 --threads 4 --timeout 120 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT:-7860}"]
