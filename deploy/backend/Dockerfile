FROM python:3.11-slim

RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY backend backend
RUN mkdir -p logs vector_db \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
