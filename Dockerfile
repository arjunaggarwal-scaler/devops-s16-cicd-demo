# ---- Session 16 CI/CD demo: calculator web API ----
FROM python:3.13-slim

# Build-time metadata (passed by the CI/CD pipeline)
ARG GIT_SHA=local
ENV GIT_SHA=${GIT_SHA} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

LABEL org.opencontainers.image.title="s16-calculator-api" \
      org.opencontainers.image.description="Session 16 CI/CD demo - Flask calculator API" \
      org.opencontainers.image.source="https://github.com/arjunaggarwal-scaler/devops-s16-cicd-demo"

WORKDIR /app

# Install dependencies first so this layer is cached between builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app/

# Run as an unprivileged user
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "app.main:app"]
