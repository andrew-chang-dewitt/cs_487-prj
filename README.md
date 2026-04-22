# CS487 Team E Software Engineering Project

## Overview

This project is a full-stack application consisting of:

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Frontend**: (\*\*\*to be implemented)

The backend exposes a REST API that serves JSON and communicates with a PostgreSQL database.

---

## Running the Project (Using Docker)

This project is fully containerized. You should not need to install Python, dependencies, or PostgreSQL locally.

### Prerequisites

- Install Docker Desktop - https://www.docker.com/products/docker-desktop/
- Ensure Docker Desktop is open and functional

  ***

## Start the application

From the **root directory** of the project, run:

```bash
docker compose up --build
```

This will:

- Build the backend container
- Start the PostgresSQL database
- Start the FastAPI server

### Dev services

If you want to just run the database service in docker (i.e. when doing development work on the backend application), run:

```bash
docker compose -f db.docker-compose.yml up
```

Then start the desired services separately, providing the necessary database connection information.

---

## Access the application

Once running, open your browser:

- Backend API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

Use /docs to test endpoints interactively

---

## How to use the API

1. Go to http://localhost:8000/docs
2. Click any endpoint
3. Click "Try it out"
4. Click "Execute"

You will see the response immediately.

---

## Stopping the project

Press: CTRL + C

Then run:

```bash
docker compose down
```

Rebuild with:

```bash
docker compose down
docker compose up --build
```

---

## Common Issues and Fixes

"docker: command not found"
Docker is not installed or not running.

Port 800 alread in use
Another application is using the port. Close the other application or change the port in the docker-compose.yml

Changes not showing:
Rebuild the containers(described in previous section)

---

## Development without Docker(Optional)

If you prefer to run locally/ok with setting up dependencies manually:

```bash
cd backend uv run fastapi dev src
```

Then open: http://127.0.0.1:8000/docs

You will need:

- Python installed
- uv installed
- A running PostgresSQL instance

---

## More Notes

- Always run from root directory
- Use Docker unless you need local development
- If something breaks or dependencies change, rebuild containers with --build
