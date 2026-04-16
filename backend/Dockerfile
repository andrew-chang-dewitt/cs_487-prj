# official Python image
FROM python:3.13-slim

# all commands will run from /app directory
WORKDIR /app

# install uv 
RUN pip install uv

# copying over all backend files into container
COPY . . 

# install dependencies from pyproject.toml
RUN uv sync

# exposing port 8000
EXPOSE 8000

# host 0.0.0.0 allows external access
# port 8000 matches exposed port
CMD ["uv", "run", "fastapi", "run", "src", "--host", "0.0.0.0", "--port", "8000"] # Run FastAPI app in "production mode"
