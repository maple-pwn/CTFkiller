FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --shell /bin/bash --create-home appuser

# Copy dependency files (if they exist)
COPY pyproject.toml* requirements*.txt* /app/

# Install Python dependencies if files exist
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    elif [ -f pyproject.toml ]; then \
        pip install --no-cache-dir .; \
    fi

# Copy application code
COPY --chown=appuser:appgroup . /app

# Switch to non-root user:
USER appuser

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["python","-m","uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
