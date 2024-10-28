# Backend Dockerfile
# Use an official Python runtime as a base image
FROM python:3.11-slim

# Install SQLite
RUN apt-get update && apt-get install -y sqlite3

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port the app runs on
EXPOSE 8857

# Command to run the application with SSL
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8857", "--reload", "--ssl-keyfile=certs/server_unencrypted.key", "--ssl-certfile=certs/server.crt"]
