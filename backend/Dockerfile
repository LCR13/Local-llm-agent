# Use an official CUDA runtime as a parent image
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Set the working directory in the container
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 and pip
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    libgomp1 \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
    && rm -rf /var/lib/apt/lists/*

# Create a symbolic link for python3.11 to python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Install Poetry
RUN pip install poetry

# Disable virtualenv creation in Poetry
RUN poetry config virtualenvs.create false

# Install llama-cpp-python with CUDA support before installing other dependencies to leverage Docker cache
RUN pip install llama-cpp-python \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

# Copy configuration files first to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

WORKDIR /app

# Install dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app

# Запуск
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]