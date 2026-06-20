# Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the cloud container
WORKDIR /app

# Copy the requirements file and install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your local application code into the container
COPY . /app/

# Expose the standard port Django uses in production environments
EXPOSE 8000

# Fire up the production-grade Gunicorn server engine
CMD ["gunicorn", "gastro_backend.wsgi:application", "--bind", "0.0.0.0:8000"]