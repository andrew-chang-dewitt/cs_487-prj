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
# generate unique app signing key
RUN echo -n "finance jwt" | sha256sum | awk '{ print $1 }' > .secrets/app_key.txt

# install dependencies from pyproject.toml
RUN uv sync

# host 0.0.0.0 allows external access
# port 8000 matches exposed port
# Run FastAPI app in "production mode"
CMD ["uv", "run", "fastapi", "run", "src", "--host", "0.0.0.0", "--port", "8000"]
