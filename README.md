
# TableMaker & Quote AI Integration API

A production-ready FastAPI backend that provides secure, idempotent APIs for table generation and AI-powered quote/chat responses.
The system supports local AI inference for development and cloud AI inference for production, with a fully automated CI/CD pipeline and PostgreSQL persistence.

Live link:https://tablemaker-zahraquote-ai-integration.onrender.com
---

## Table of Contents
- JWT Authentication (stateless, secure)

-  Idempotent Request Handling

    - Prevents duplicate processing

    - Detects conflicting payloads with the same idempotency key

-  External API Integration( Zahra-Quotes-API)

-  AI Integration

    - Local development: Ollama (no API key required)

    - Production: Hugging Face Inference API

-  Dynamic Table Generation

    - HTML tables

    - Markdown tables

-  PostgreSQL Database (Render-managed)

-  Robust Test Suite

    - Unit tests

    - Integration tests

    - SQLite in-memory DB for CI

-  Rate Limiting (SlowAPI)

-  Health Checks

-  Deployed on Render

-  CI/CD via GitHub Actions
---

## Architecture Overview
```bash
     Client (React / Postman)
        |
        v
     FastAPI Backend (Render)
     ├── JWT Auth
     ├── Idempotency Layer
     ├── Rate Limiting Middleware
     ├── AI Provider Switch
     │     ├── Ollama (local)
     │     └── Hugging Face (production)
     ├── PostgreSQL (Render)
     └── Health Checks

  ```
---

## Project Structure
```bash
        app/
      ├── main.py
      ├── api/
      │   ├── routers/
      │   │   ├── auth.py
      │   │   ├── health.py
      │   │   ├── openai.py
      │   │   ├── quotes.py
      │   │   └── table_request_router.py
      │   ├── middleware.py
      │   ├── exceptions.py
      │   └── rate_limit.py
      ├── core/
      │   ├── config.py
      │   └── security.py
      ├── db/
      │   ├── session.py
      │   └── tableModels.py
      ├── services/
      │   ├── idempotency.py
          └── table_service.py
      tests/
      ├── unit/
      ├── integration/
      └── conftest.py

  ```

---


## Authentication
```bash
      GET /generate-token

```
   Response
```bash
      {
      "token": "jwt-token-here"
      }

```
   Use this token in subsequent requests:
```bash
      Authorization: Bearer <token>

```
---

## Idempotency
   All write operations support idempotency using the header:
```bash
      Idempotency-Key: <unique-key>

 ```
## Behavior:
  - Same key + same payload → cached response returned

  - Same key + different payload → 409 Conflict



---
## AI Provider Switching
The backend dynamically selects the AI provider using an environment variable.

# Local Development (Ollama)
```bash
    AI_PROVIDER=ollama

```
  - Requires Ollama running locally

  - No API key required

  - Ideal for learning and offline development
# Production (Hugging Face)

```bash
    AI_PROVIDER=huggingface
    HF_API_TOKEN=your_token_here

```
  - Used on Render

  - Stable, scalable inference


---
## Testing Strategy
  - CI Database: SQLite in-memory

  - Production Database: PostgreSQL

  - Shared connection pool using StaticPool for SQLite

  - Tables auto-created and destroyed per test session
# Run tests locally
```bash
    pytest
```

---

## CI/CD Pipeline
# GitHub Actions
  - Runs on every push to main

  - Installs dependencies

  - Injects test environment variables

  - Executes full test suite

  - Prevents broken deployments

# Deployment (Render)
# tablemaker-zahraquote-ai-integration
  - Platform: Render Web Service

  - Runtime: Python 3

  - Database: Render PostgreSQL

  - Health check enabled

# Required Environment Variables (Render)
```bash
    DATABASE_URL=postgresql://...
    JWT_SECRET=
    JWT_ALGORITHM=HS256
    AI_PROVIDER=huggingface
    HF_API_TOKEN=

```

---

## Health Check
```bash
    GET /health

```
Response:
```bash
    { "status": "ok" }

```
Used by Render to ensure service availability.

---

## API Documentation
Interactive Swagger UI available at:
```bash
    /docs

```

---

## Security & Best Practices
  - No secrets committed to source control

  - Environment-based configuration

  - Strict error handling

  - Production-safe defaults

  - Separation of test vs production behavior

---

## Key Engineering Challenges Solved
  - Migrated from MySQL → PostgreSQL without breaking tests

  - Fixed SQLite in-memory isolation using StaticPool

  - Ensured CI stability with environment injection

  - Implemented real-world idempotency guarantees

  - Safely handled AI provider differences across environments

---

## Author
# Zahra Shefa

TableMaker & Quote AI Integration API / Full-Stack Engineer

Deployed, tested, and production-ready API with AI integration





