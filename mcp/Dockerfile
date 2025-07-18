# MCP Server Dockerfile
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

# Copy MCP source code
COPY mcp/src/ ./mcp/src/

# Create necessary directories
RUN mkdir -p /app/projects /app/run

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_PORT=6968
ENV API_BASE_URL=http://api:6969

# Expose port
EXPOSE 6968

# Health check - MCP server doesn't have a standard health endpoint, so check process
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep -f "mcp.src" || exit 1

# Run the MCP server
CMD ["python", "-m", "mcp.src.http_server"]