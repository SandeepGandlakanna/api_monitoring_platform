# API Monitoring & Observability Platform

A full-stack API monitoring platform built with Python, FastAPI,
SQLModel, SQLite, Streamlit, and Docker.

## Features

- User registration and JWT authentication
- Secure password hashing with Argon2
- Create, update, and delete API monitors
- Configurable monitoring intervals
- Background API monitoring scheduler
- HTTP status code monitoring
- Response-time measurement
- Monitoring history
- Uptime and response-time statistics
- Failure detection
- Automatic alert creation
- Automatic alert resolution after recovery
- User-based monitor ownership
- Streamlit dashboard
- Docker and Docker Compose support
- SQLite database persistence
- Automated tests with pytest

## Tech Stack

- Python
- FastAPI
- SQLModel
- SQLite
- HTTPX
- JWT
- pwdlib / Argon2
- Streamlit
- Pandas
- Plotly
- Docker
- Docker Compose
- Pytest

## Architecture

```text
                    ┌─────────────────────┐
                    │     Streamlit       │
                    │     Dashboard       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │       REST API      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      SQLModel       │
                    │   Service Layer     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       SQLite        │
                    │      Database       │
                    └─────────────────────┘

                    Background Scheduler
                            │
                            ▼
                    External API Endpoints
                            │
                            ▼
                    Check Results + Alert


