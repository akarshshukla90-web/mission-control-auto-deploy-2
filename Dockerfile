# Dockerfile for deploying Mission Control to Render or Hugging Face Spaces
FROM python:3.10-slim

# Install necessary system dependencies (for agents using Chromium/Selenium if applicable)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all mission control files
COPY . .

# Ensure the static and workspace directories exist
RUN mkdir -p static workspace/knowledge workspace/knowledge_base workspace/business_data

# The server.py listens on port 8888 natively. We can expose it.
EXPOSE 8888

# Command to run the application
CMD ["python", "-u", "server.py"]
