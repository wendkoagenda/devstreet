#!/bin/sh
set -e

echo "[projet-backend] entrypoint starting — if you see this, CMD/entrypoint is running (check the container logs)."

# Aucune valeur par defaut : tout doit venir des variables d'environnement du conteneur.
for var in DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD SECRET_KEY JWT_SIGNING_KEY ADMIN_EMAIL ADMIN_PASSWORD DEBUG ALLOWED_HOSTS CORS_ALLOWED_ORIGINS CSRF_TRUSTED_ORIGINS FRONTEND_URL EMAIL_BACKEND DEFAULT_FROM_EMAIL USE_X_FORWARDED_PROTO ENABLE_API_DOCS ENABLE_ADMIN USE_S3; do
  eval "val=\$$var"
  if [ -z "$val" ]; then
    echo "ERROR: $var is not set or empty."
    echo "Define it in the container environment (runtime). No fallback in entrypoint."
    exit 1
  fi
done

case "$DB_PORT" in
  ''|*[!0-9]*)
    echo "ERROR: DB_PORT must be a numeric port (e.g. 5432), got: '$DB_PORT'"
    exit 1
    ;;
esac

# Limite de temps : evite une boucle infinie si DB_HOST est faux (ex. typo, mauvais nom DNS).
DB_WAIT_MAX_SEC=120
echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT} (max ${DB_WAIT_MAX_SEC}s)..."
attempt=0
while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge "$DB_WAIT_MAX_SEC" ]; then
    echo "ERROR: PostgreSQL still not reachable at ${DB_HOST}:${DB_PORT} after ${DB_WAIT_MAX_SEC}s."
    echo "If logs showed getaddrinfo / name resolution: DB_HOST is not a valid hostname inside this container (wrong value or not on the same Docker network as Postgres)."
    echo "Use the hostname of the PostgreSQL server as seen from this container (the service name on the same Docker network, or the VM address)."
    exit 1
  fi
  sleep 1
done

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
