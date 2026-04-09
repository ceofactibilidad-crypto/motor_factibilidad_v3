FROM python:3.11-slim

# Install system dependencies required by some packages (e.g. psycopg2, playwright)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the backend source and its sibling frontend (referenced as ../frontend in main.py)
COPY factibilidad_v3/backend/ ./backend/
COPY factibilidad_v3/frontend/ ./frontend/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Set the working directory to the backend so all relative imports resolve correctly
WORKDIR /app/backend

EXPOSE 8000

# Use $PORT if provided by Railway, otherwise default to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
