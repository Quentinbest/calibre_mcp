FROM python:3.11-slim

# Install system dependencies and Calibre
# Calibre is required for calibredb and ebook-convert
RUN apt-get update && apt-get install -y \
    calibre \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the server
CMD ["python", "server.py"]
