# Build stage for frontend
FROM node:20-alpine as frontend-build

WORKDIR /app/frontend

COPY src/frontend/package*.json ./
RUN npm ci

COPY src/frontend/ ./
RUN npm run build

# Main stage
FROM python:3.12-slim

# Install system dependencies for scapy and packet sniffing
RUN apt-get update && apt-get install -y \
    tcpdump \
    libpcap-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code (selective to avoid unnecessary files)
COPY src/ ./src/
COPY config.yaml .
COPY generate_anomalies.py .

# Copy trained models
COPY trained_models/ ./trained_models/

# Copy built frontend from build stage
COPY --from=frontend-build /app/frontend/dist ./src/frontend/dist

# Create logs directory
RUN mkdir -p logs

# Expose the port for the API
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TF_CPP_MIN_LOG_LEVEL=3

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/alerts', timeout=5)" || exit 1

# Command to run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
