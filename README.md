# Taxi API

![CI](https://github.com/bogdan0089/Taxi-/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Async ride-hailing REST API built with FastAPI, PostgreSQL, Redis, Stripe, and Celery.

## Stack

- **FastAPI** — async REST API
- **PostgreSQL + SQLAlchemy** — async ORM with Alembic migrations
- **Redis** — caching and token storage
- **Stripe** — payment processing
- **Celery** — background tasks (email verification)
- **JWT** — authentication with access/refresh tokens
- **WebSockets** — real-time connection manager
- **Docker** — containerized services

## Architecture

Clean layered architecture with dependency injection:

```
app/
├── enums/          # Role, Status
├── core/           # Config, exceptions, redis, logger, celery
├── db/
│   └── postgres/
│       ├── models/       # User, Trip, Rating
│       ├── repository/   # BaseRepository + domain repositories
│       └── session.py    # Async session factory
├── dto/
│   ├── input/      # Request DTOs
│   └── output/     # Response DTOs (no raw ORM in responses)
├── services/       # Business logic
├── routers/        # FastAPI routers with Depends injection
├── tasks/          # Celery tasks
└── utils/          # Helpers
```

## Features

- **Auth** — register, login, logout, email verification, JWT refresh
- **Users** — profile management, account deactivation
- **Trips** — create, accept, complete, cancel with status transitions
- **Payments** — Stripe PaymentIntent integration
- **Ratings** — per-trip driver ratings with avg calculation and Redis cache
- **Admin** — user management, trip overview, active/verified users

## Getting Started

### 1. Clone and set up environment

```bash
git clone https://github.com/bogdan0089/Taxi-.git
cd Taxi-
cp .env.example .env
```

Fill in all values — see `.env.example` for the full list of required variables.

### 2. Start services with Docker

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

## Running Tests

### 1. Start test database

```bash
docker-compose -f docker/docker-compose.yml up -d db
```

### 2. Run migrations on test DB

```bash
DB_HOST=localhost DB_PORT=5434 DB_NAME=uber_db_test alembic upgrade head
```

### 3. Run tests

```bash
pytest tests/ -v
```

19 integration tests covering auth, users, trips, ratings, and admin endpoints.

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | — |
| POST | `/auth/login` | Login, get tokens | — |
| POST | `/auth/logout` | Logout | ✅ |
| POST | `/auth/refresh/{token}` | Refresh access token | — |
| GET | `/auth/verify/{token}` | Verify email | — |

### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/{id}` | Get user profile | ✅ |
| PATCH | `/users/me` | Update profile | ✅ |
| DELETE | `/users/me` | Deactivate account | ✅ |

### Trips
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/trips/` | Create trip | Passenger |
| GET | `/trips/available` | Get available trips | Driver |
| GET | `/trips/my` | Get my trips | ✅ |
| POST | `/trips/{id}/accept` | Accept trip | Driver |
| POST | `/trips/{id}/complete` | Complete trip | Driver |
| POST | `/trips/{id}/cancel` | Cancel trip | ✅ |

### Payment
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/payment/method` | Save payment method | ✅ |

### Ratings
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/ratings/` | Rate driver | Passenger |
| GET | `/ratings/driver/{id}/avg` | Get driver avg rating | ✅ |

### Admin
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/users` | List all users | Admin |
| GET | `/admin/trips` | List all trips | Admin |
| GET | `/admin/active/verified` | Active verified users | Admin |

### Health
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | — |
