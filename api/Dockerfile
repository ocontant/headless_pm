# API Server Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared components first
COPY shared/ ./shared/

# Copy requirements and install dependencies
COPY setup/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source code
COPY api/src/ ./api/src/

# Create necessary directories
RUN mkdir -p /app/projects /app/run

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=6969
ENV DATABASE_URL=sqlite:///app/database/headless-pm.db

# Expose port
EXPOSE 6969

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6969/health || exit 1

# Run the application
CMD ["python", "-m", "api.src.main"]