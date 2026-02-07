# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY wled_mcp/ ./wled_mcp/
COPY README.md ./
COPY config.example.yaml ./

# Install the package
RUN pip install --no-cache-dir -e .

# Create config directory
RUN mkdir -p /root/.wled_mcp

# Set environment variable for MCP server
ENV PYTHONUNBUFFERED=1

# Optional: Set config file location (can be overridden)
# ENV WLED_CONFIG_FILE=/root/.wled_mcp/config.yaml

# Run the MCP server
CMD ["python", "-m", "wled_mcp.server"]
