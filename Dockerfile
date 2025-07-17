FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server code
COPY crossref_mcp.py .

# Make the script executable
RUN chmod +x crossref_mcp.py

# Expose the port (if needed for HTTP/SSE)
EXPOSE 8000

# Run the MCP server
CMD ["python", "crossref_mcp.py"]
