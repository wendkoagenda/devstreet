FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# netcat : attente de PostgreSQL dans entrypoint.sh (psycopg2-binary embarque libpq : pas de compilateur)
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Dépendances Python (versions figées)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Utilisateur non-root
RUN useradd --create-home --uid 10001 app

COPY --chown=app:app . .

COPY --chown=app:app entrypoint.sh /entrypoint.sh
RUN chmod 0555 /entrypoint.sh

USER app

EXPOSE 8000

CMD ["/entrypoint.sh"]
