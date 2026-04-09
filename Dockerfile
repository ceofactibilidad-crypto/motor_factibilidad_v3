FROM python:3.11-slim

# Install system dependencies required by some packages (e.g. psycopg2, playwright)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Keep working directory at /app so that relative paths like ../frontend resolve
# correctly when uvicorn runs from /app/backend (../frontend → /app/frontend)
WORKDIR /app

# Copy both backend and frontend so the container layout mirrors the source tree:
#   /app/backend/  ← main.py, requirements.txt, etc.
#   /app/frontend/ ← static files served by FastAPI
COPY factibilidad_v3/backend/ ./backend/
COPY factibilidad_v3/frontend/ ./frontend/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

EXPOSE 8000

# Change into /app/backend before starting so Python resolves local module imports
# (models, database, routers…) while ../frontend still points to /app/frontend.
# Use $PORT if provided by Railway, otherwise default to 8000.
CMD cd /app/backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
