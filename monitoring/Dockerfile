FROM python:3.11-slim

RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./monitoring /app
RUN chown -R appuser:appgroup /app

USER appuser

ENV BACKEND_URL=http://backend:8000

EXPOSE 8502

CMD ["streamlit", "run", "dashboard.py", "--server.port", "8502", "--server.address", "0.0.0.0", "--server.headless", "true"]
