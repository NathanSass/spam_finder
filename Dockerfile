# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code


# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* /code/

# Install poetry
RUN pip install --no-cache-dir poetry

# Install dependencies
RUN poetry install --no-root

# Copy the application code into the container
COPY app /code/app
COPY agents /code/agents
COPY score_evaluator /code/score_evaluator
COPY .env /code/.env

# Expose port 80
EXPOSE 80

# Command to run the application using uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
