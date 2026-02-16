#!/bin/sh
set -e

# Ждём готовности PostgreSQL (показываем ошибку при сбое)
echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432} (user ${POSTGRES_USER}, db ${POSTGRES_DB})..."
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q'; do
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST}..."
  sleep 2
done
echo "PostgreSQL is ready."

# Миграции Alembic
echo "Running migrations..."
alembic upgrade head
echo "Migrations done."

exec "$@"
