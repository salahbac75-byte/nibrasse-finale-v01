# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# build-essential is often needed for compiling Python packages like chromadb dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
# Railway will override this with the $PORT environment variable
ENV PORT=8000
EXPOSE $PORT

# Run app.py when the container launches
# We use the shell form to allow variable expansion for $PORT
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
