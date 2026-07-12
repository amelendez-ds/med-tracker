# 1. We start with a small, clean, standard Linux computer with Python 3.12 installed
FROM python:3.12-slim

# 2. We tell Docker to do all following work inside a folder called /app
WORKDIR /app

# 3. Install uv (package manager)
RUN pip install uv

# 4. Copy everything from my Mac's med-tracker folder into the container's /app folder
COPY . /app

# 5. Tell uv to install all the dependencies exactly as we have them in the pyproject.toml
RUN uv sync

# 6. Open up port 8000 so the container can talk to my Mac's web browser
EXPOSE 8000

# 7. The command to start the server when the container turns on
# Note: We use --host 0.0.0.0 in Docker so it is accessible outside the container
CMD ["uv", "run", "uvicorn", "med_tracker.main:app", "--host", "0.0.0.0", "--port", "8000"]