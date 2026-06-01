# 1. Use an official, lightweight Python base image from Docker Hub
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files to disk and ensure logs print instantly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the active working directory inside the virtual container container
WORKDIR /app

# 4. Install essential Linux system utilities required for compilation and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file into the image container filesystem
COPY requirements.txt /app/

# 6. Upgrade pip and install all Python application packages
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copy the remaining local project files straight into the application container
COPY . /app/