FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (cached layer)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv (cached layer)
RUN pip install --no-cache-dir uv

# Copy only requirements first (maximize cache hit on app code changes)
COPY requirements.txt .

# Install Python dependencies using uv (cached unless requirements change)
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code (changes frequently, put last)
COPY . .

# Expose port
EXPOSE 8100

# Run migrations and start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100", "--reload"]
