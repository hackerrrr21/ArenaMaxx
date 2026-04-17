# STAGE 1: Build the Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# STAGE 2: Build the Backend & Runtime
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Setup Backend
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port (Internal only, Cloud Run overrides this)
EXPOSE 8080

# Start command
WORKDIR /app/backend
CMD gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
