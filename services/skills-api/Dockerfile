FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scorecard engine (shared logic)
COPY scorecard_engine.py main.py ./

# Mount skills at runtime via volume
ENV SKILLS_ROOT=/app/skills
ENV SKILLS_INDEX=/app/skills_index.json

RUN useradd -m apiuser
USER apiuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
