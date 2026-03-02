#!/bin/sh
# Поднять все сервисы одной командой из корня проекта.
# Миграции выполняются автоматически при старте backend.
set -e
cd "$(dirname "$0")"
docker compose up -d --build
echo ""
echo "Сервисы запущены:"
echo "  API:      http://localhost:8000  (документация: /docs)"
echo "  AI Chat:  http://localhost:8001"
echo ""
echo "Остановка: docker compose down"
