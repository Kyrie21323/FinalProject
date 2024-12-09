# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY . .

# Let Cloud Run handle the port - remove EXPOSE
CMD ["sh", "-c", "uvicorn database_api:app --host 0.0.0.0 --port $PORT"]