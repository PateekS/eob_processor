# Use an official Python base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \          # For PDF-to-image conversion
    tesseract-ocr \          # For OCR
    tesseract-ocr-eng \      # English language data for Tesseract
    libgl1-mesa-glx \        # Required for OpenCV
    libglib2.0-0 && \        # General-purpose dependency
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY . /app/

# Expose the Flask app's port (default: 5000)
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]
