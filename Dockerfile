# Use official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    BRAIN_DATA_DIR="/data" \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies (build-essential for hnswlib/chromadb, libgl/libglib for opencv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Create volume mount point for persistent data directory
RUN mkdir -p /data

# Expose port (Render overrides this, but good for local/Docker Compose)
EXPOSE 8000

# Start server using uvicorn launcher in api_server
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]
