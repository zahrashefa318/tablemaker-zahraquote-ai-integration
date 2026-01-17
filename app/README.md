# ZahraTableMaker — AI-assisted table API (with safe fallback)

Turn a list of JSON objects into a styled HTML or Markdown table.  
Column order is suggested by OpenAI Chat Completions; if the AI call fails (no key, quota, etc.), the service falls back to a deterministic “union of keys” order so your API still works.

---

## Table of Contents
- [Features](#features)  
- [Requirements](#requirements)  
- [Environment Variables](#environment-variables)  
- [Installation & Start](#installation-and-start)  
- [Endpoints](#endpoints)  
  - [Health](#health)  
  - [Smart Column Suggestion](#smart-column-suggestion-ai-with-fallback)  
  - [Make a Table (AI-assisted; safe fallback)]
  - [Demo with JSONPlaceholder](#demo-with-jsonplaceholder) 
  (#make-a-table-ai-assisted-safe-fallback)  
- [API Schema](#api-schema)  
- [Examples](#examples)  
  - [HTML Table](#html-table)  
  - [Markdown Table](#markdown-table)  
  - [Browser Usage](#using-from-the-browser)  

---

## Features
- `POST /ZahraTable` — Returns an HTML or Markdown table from your JSON data.  
- `POST /smart-columns` — Asks the OpenAI API to propose a human-friendly column order; if AI fails, returns the union of keys.  
- API key header protection using FastAPI’s `APIKeyHeader` + `Security` (visible in `/docs`).  
- Built with FastAPI.  
- CORS enabled so your browser `fetch` works across origins.  
- Helpful error messages for validation and AI failures.  
- **Demo endpoint** that fetches data from a public fake API (`https://jsonplaceholder.typicode.com/users`) via HTTPX for quick testing or demonstration.

---

## Requirements
- Python 3.10+  
- Packages:  
    - fastapi
    - uvicorn
    - openai
    - httpx

---


## Environment Variables
- `OPENAI_API_KEY` – your OpenAI API key (used by `/smart-columns` and `/ZahraTable` internally).  
- `Z_API_KEY` – the value expected in request header `z_api_key` (defaults to `dev-key` if not set).

---

## Installation & Start
1. Create a `requirements.txt` with the required packages.  
2. Install dependencies:
 ```bash
 python -m pip install -r requirements.txt
 ```
3. Set environment variables:
    - On Windows PowerShell:
    ```bash
    $env:OPENAI_API_KEY = "sk-..."
    $env:Z_API_KEY       = "dev-key"
    ```
    - On macOS/Linux:
    ```bash
        export OPENAI_API_KEY="sk-..."
        export Z_API_KEY="dev-key"
    ```
4. Start the server:
    - uvicorn main:app --host 0.0.0.0 --port 8000 --reload

---
## Endpoints
# Health

# GET /health
# Response:
```bash
    { "ok": true }
```
# Smart column suggestion (AI with fallback)

# POST /smart-columns
# Headers:
```bash
    z_api_key: "zahra-key"
```
# Body:
```bash
    { 
  "sample": [ { … }, { … } ] 
}
```
# Response (200):
```bash
    { 
  "columns": ["first_name","last_name","email", …], 
  "ai_used": true | false 
}
```
# Demo with JSONPlaceholder
- GET /demo/jsonplaceholder
This endpoint integrates with the public fake API at https://jsonplaceholder.typicode.com/users (a free resource for fake data for testing and prototyping). 

It uses HTTPX’s AsyncClient to fetch user data and then returns an HTML table with selected fields (name, email, company).
# Example snippet:
```bash
    @app.get("/demo/jsonplaceholder")
async def demo_jsonplaceholder():
    url = "https://jsonplaceholder.typicode.com/users"
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        users = r.json()
    rows = [
      {"name": u.get("name"), "email": u.get("email"), "company": (u.get("company") or {}).get("name")}
      for u in users
    ]
    columns = ["name", "email", "company"]
    return Response(content=to_html(rows, columns), media_type="text/html")

```
# Make a table (AI-assisted; safe fallback)

# POST /ZahraTable
# Headers:
```bash
    z_api_key: "zahra-key"
```
# Body:
```bash
    {
  "format": "html" | "markdown",
  "columns": [ … ]?,              # optional manual order
  "data": [ { … }, { … }, … ]     # list of JSON objects
}
```
## API Schema
```bash
    # /smart-columns
POST /smart-columns:
  headers:
    z_api_key: string (required)
  body:
    sample: array of objects
  response:
    200:
      columns: array of strings
      ai_used: boolean
    401: unauthorized (invalid/missing z_api_key)
    422: validation error (missing/invalid sample)

# /ZahraTable
POST /ZahraTable:
  headers:
    z_api_key: string (required)
  body:
    format: enum("html","markdown")
    columns: (optional) array of strings
    data: array of objects (required)
  response:
    200: string (HTML or Markdown)
    401: unauthorized
    422: validation error (missing/invalid format/data)
    500: internal error (AI failure + fallback error)

# /demo/jsonplaceholder
GET /demo/jsonplaceholder:
  response:
    200: HTML table (content-type text/html)
    500: internal error (unexpected failure)
```
## HTML Table
```bash
    curl -i -X POST http://127.0.0.1:8000/ZahraTable \
  -H "Content-Type: application/json" \
  -H "z_api_key: dev-key" \
  -d '{
    "format":"html",
    "data":[
      {"first_name":"Ana","last_name":"Lopez","email":"ana@example.com"},
      {"first_name":"Bob","email":"bob@example.com","role":"admin"},
      {"email":"cara@example.com","first_name":"Cara","last_name":"Zed"}
    ]
  }'
```
## Markdown Table
```bash
    curl -i -X POST http://127.0.0.1:8000/ZahraTable \
  -H "Content-Type: application/json" \
  -H "z_api_key: dev-key" \
  -d '{
    "format":"markdown",
    "data":[
      {"name":"Alice","age":30},
      {"name":"Bob","age":25,"city":"NYC"}
    ]
  }'
```
## Using from the Browser
```bash
    <script>
const body = {
  format: "html",
  data: [
    { first_name: "Ana", last_name: "Lopez", email: "ana@example.com" },
    { first_name: "Bob", email: "bob@example.com", role: "admin" }
  ]
};

const r = await fetch("https://my-host/ZahraTable", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "z_api_key": "zahra-key"
  },
  body: JSON.stringify(body)
});

document.getElementById("out").innerHTML = await r.text();
</script>
```




