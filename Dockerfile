# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src  /app

# Copy the images folder into the container
COPY images /app/images

# Specify the command to run the application
CMD ["python", "jericho.py"]