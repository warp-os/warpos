FROM python:3.11-slim

WORKDIR /app

# Install warpos from PyPI
RUN pip install --no-cache-dir warpos

# Copy example agent
COPY examples/basic.py agent.py

# Expose port
EXPOSE 10000

# Run the agent server
CMD ["python", "-c", "from agent import agent; agent.serve(host='0.0.0.0', port=10000)"]
