# official Python image
FROM python:3.13-slim

# all commands will run from /app directory
WORKDIR /app

# install system dependencies (directly from GitHub repo)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# install uv (for dependency resolution)
RUN pip install uv

# copying over backend files into container (.dockerignore will ignore .venv and more)
COPY . . 

# install dependencies from pyproject.toml
RUN uv sync

# exposing port 8000
# EXPOSE 8000

# host 0.0.0.0 allows external access
# port 8000 matches exposed port
# Run FastAPI app in "production mode"
CMD ["uv", "run", "fastapi", "run", "src", "--host", "0.0.0.0", "--port", "8000"]
