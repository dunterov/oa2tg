# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first, then install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY oa2tg.py .

# Specify the command to run the app
ENTRYPOINT ["python", "oa2tg.py"]
