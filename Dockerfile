# Use the official Python image as a base
FROM python:3.11.2-slim

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install dependencies
COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src .

# Expose the port on which the app will run
EXPOSE 5000

COPY wait-for-db.sh ./

# Run the Flask application
CMD ["python", "main.py"]
