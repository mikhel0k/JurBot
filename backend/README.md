# JurBot Backend

FastAPI-бэкенд для управления компаниями и сотрудниками.

## Требования

- Python 3.11+
- Docker и Docker Compose
- Gmail-аккаунт (или SMTP) для отправки кодов подтверждения

## Установка

```bash
pip install -r requirements.txt
```

## Конфигурация

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Заполните переменные в `.env` (PostgreSQL, Redis, Gmail и т.д.).

3. Создайте JWT-ключи:
   ```bash
   mkdir -p jwt_tokens
   openssl genrsa -out jwt_tokens/jwt-private.pem 2048
   openssl rsa -in jwt_tokens/jwt-private.pem -pubout -out jwt_tokens/jwt-public.pem
   ```

## Запуск БД и Redis

```bash
docker-compose up -d
```

## Миграции

```bash
alembic upgrade head
```

## Запуск приложения

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Или:

```bash
python main.py
```

## Тесты

1. Убедитесь, что запущены `postgres_test` и `redis` (или оба контейнера).

2. Запуск тестов:
   ```bash
   PYTHONPATH=. pytest tests/ -v
   ```

3. С покрытием:
   ```bash
   pip install pytest-cov
   PYTHONPATH=. pytest tests/ -v --cov=app
   ```

## Структура

```
app/
├── api/
│   ├── health.py      # /health, /ready
│   └── v1/            # Auth, Company, Employee
├── core/              # config, database, security, rate_limit
├── models/            # SQLAlchemy
├── repository/        # Репозитории
├── schemas/           # Pydantic
└── services/          # Бизнес-логика
```

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /health | Liveness probe |
| GET | /ready | Readiness (PostgreSQL + Redis) |
| POST | /v1/auth/register | Регистрация (шаг 1) |
| POST | /v1/auth/register/confirm | Подтверждение регистрации |
| POST | /v1/auth/login | Вход (шаг 1) |
| POST | /v1/auth/login/confirm | Подтверждение входа |
| POST | /v1/auth/logout | Выход |
| POST | /v1/company/ | Создать компанию |
| GET | /v1/company/ | Получить компанию |
| PATCH | /v1/company/ | Обновить компанию |
| GET | /v1/employee/ | Список сотрудников |
| POST | /v1/employee/ | Добавить сотрудника |
| GET | /v1/employee/{id} | Получить сотрудника |
| PATCH | /v1/employee/{id} | Обновить сотрудника |
| DELETE | /v1/employee/ | Уволить сотрудников |

## Rate limiting

- `/auth/register` и `/auth/login`: 10 запросов в минуту с одного IP (429 при превышении).
