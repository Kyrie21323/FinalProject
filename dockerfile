# Use Python base image
FROM python:3.9-slim

# Set working directory (assuming /app, but you might have something different!)
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI server (this should be exactly what you do when working locally)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]