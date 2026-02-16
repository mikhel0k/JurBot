# JurBot

Бэкенд для управления компаниями и сотрудниками с двухфакторной аутентификацией (код по email), JWT в httponly cookies и кэшированием в Redis.

## Стек

- **FastAPI** — API
- **PostgreSQL** + **SQLAlchemy 2.0** (async) — БД
- **Redis** — кэш и хранение кодов подтверждения
- **Alembic** — миграции
- **Pydantic** — валидация и сериализация
- **JWT (RS256)** — токены в cookies

## Структура проекта

```
JurBot/
├── backend/
│   ├── app/
│   │   ├── api/v1/      # Эндпоинты
│   │   ├── core/        # Конфиг, БД, безопасность
│   │   ├── models/      # SQLAlchemy модели
│   │   ├── repository/  # Репозитории
│   │   ├── schemas/     # Pydantic схемы
│   │   └── services/    # Бизнес-логика
│   ├── migrations/      # Alembic
│   ├── tests/
│   └── main.py
└── frontend/
```

## Требования

- Python 3.11+
- Docker и Docker Compose (для PostgreSQL и Redis)
- Gmail-аккаунт для отправки кодов (или настройка SMTP)

## Быстрый старт

### 1. Клонирование и настройка окружения

```bash
git clone <repo_url>
cd JurBot/backend
```

### 2. Переменные окружения

Создайте файл `.env` в каталоге `backend/`:

```bash
cp .env.example .env
```

Заполните переменные. Пример `.env.example`:

```env
# PostgreSQL (основная БД)
POSTGRES_DB=jurbot
POSTGRES_USER=jurbot
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# PostgreSQL (тестовая БД)
POSTGRES_DB_TEST=jurbot_test
POSTGRES_USER_TEST=jurbot
POSTGRES_PASSWORD_TEST=your_secure_password
POSTGRES_HOST_TEST=localhost
POSTGRES_PORT_TEST=5433

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Логирование
LOG_LEVEL=INFO

# JWT (путь к ключам RS256)
# Создайте jwt_tokens/ в backend/ и поместите туда jwt-private.pem и jwt-public.pem
# Или укажите свои пути

# Gmail для отправки кодов подтверждения
LOGIN_FOR_GMAIL=your@gmail.com
PASSWORD_FOR_GMAIL=app_password_from_google
SEND_LOGIN_CODE_EMAIL=true
```

### 3. JWT-ключи

Сгенерируйте пару ключей RS256:

```bash
mkdir -p backend/jwt_tokens
openssl genrsa -out backend/jwt_tokens/jwt-private.pem 2048
openssl rsa -in backend/jwt_tokens/jwt-private.pem -pubout -out backend/jwt_tokens/jwt-public.pem
```

### 4. Запуск PostgreSQL и Redis

```bash
cd backend
docker-compose up -d
```

### 5. Миграции

```bash
cd backend
alembic upgrade head
```

### 6. Запуск приложения

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Или:

```bash
python main.py
```

API будет доступно по адресу: **http://localhost:8000**

- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc  

## Запуск тестов

### Предварительно

1. Запустите тестовую БД: `docker-compose up -d postgres_test`
2. Убедитесь, что Redis запущен: `docker-compose up -d redis`
3. Переменные `POSTGRES_*_TEST` и `REDIS_*` должны быть заданы в `.env`

### Команда

```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

С покрытием кода:

```bash
pip install pytest-cov
PYTHONPATH=. pytest tests/ -v --cov=app
```

## Запуск всего приложения в Docker (docker compose)

Из корня проекта можно поднять все сервисы в контейнерах (PostgreSQL, Redis, MongoDB, backend, ai-chat-service). При старте backend автоматически выполняются миграции Alembic.

**Требования:** папка `backend/jwt_tokens/` с ключами JWT (см. раздел про JWT-ключи). Переменные окружения для контейнеров берутся из **`.env` в корне проекта** (Docker Compose читает только его). Удобно скопировать из backend: `cp backend/.env .env`. Если `.env` в корне нет, будут использованы значения по умолчанию (пароль БД: `jurbot`).

```bash
cd JurBot
cp backend/.env .env   # если ещё не копировали
docker compose up --build
```

- **Backend API:** http://localhost:8000 (документация: /docs)
- **AI Chat Service:** http://localhost:8001

Остановка: `docker compose down`. Данные Redis сохраняются в volume `redis_data`.

**Если в браузере не открывается:**

1. Проверьте, что контейнеры запущены: `docker compose ps`. У `jurbot_backend` и `jurbot_ai_chat` должно быть состояние `Up` (не `Restarting` и не `Exited`).
2. Посмотрите логи backend: `docker compose logs backend --tail 80`. Частые причины падения:
   - **JWT-ключи не найдены** — в `backend/jwt_tokens/` должны лежать файлы `jwt-private.pem` и `jwt-public.pem` (см. раздел «JWT-ключи» выше).
   - **Нет переменной API_TOKEN** — в `backend/.env` должна быть строка `API_TOKEN=...` (можно пустое значение для проверки, если код это допускает).
3. Логи ai-chat: `docker compose logs ai-chat-service --tail 50`.
4. После исправления перезапустите: `docker compose up -d --build`.

## Основные эндпоинты

| Путь | Описание |
|------|----------|
| GET /health | Liveness probe |
| GET /ready | Readiness (БД + Redis) |
| POST /v1/auth/logout | Выход (очистка cookies) |
| GET /v1/employee/ | Список сотрудников компании |

## Аутентификация

- Регистрация и вход — двухфакторные: после email/пароль на почту отправляется 6-значный код
- Токены выдаются в **httponly cookies**: `access_token`, `refresh_token`
- Cookies: `httponly`, `secure`, `samesite=lax`
- Access-токен: 30 минут
- Refresh-токен: 30 дней

Для эндпоинтов `/company/*` и `/employee/*` требуется аутентификация (cookies отправляются браузером автоматически).

- Rate limiting: `/auth/register` и `/auth/login` — 10 запросов/мин с одного IP (429 при превышении).

## Лицензия

MIT
