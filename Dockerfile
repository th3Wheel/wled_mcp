# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY wled_mcp/ ./wled_mcp/
COPY README.md ./

# Install the package
RUN pip install --no-cache-dir -e .

# Set environment variable for MCP server
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["python", "-m", "wled_mcp.server"]
