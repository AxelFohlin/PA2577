# Use the official Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY requirements.txt requirements.txt
COPY app.py app.py

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the service runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
