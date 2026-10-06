# ==============================================================================
# ForensiWeb Controlled Vulnerable Application — Container Definition
# ==============================================================================
# Runs strictly inside isolated forensiweb-lab-net with dropped capabilities.
# ==============================================================================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=app.routes:app \
    FLASK_ENV=development

WORKDIR /app

# Create unprivileged lab user
RUN groupadd -g 1000 labuser && \
    useradd -u 1000 -g labuser -s /bin/bash -m labuser

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=labuser:labuser . /app/

USER labuser

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
