FROM python:3.12-slim

# Install build tools for any native deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY bot.py scorecard_engine.py ./

# Non-root user for security
RUN useradd -m botuser
USER botuser

CMD ["python", "-u", "bot.py"]
