# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OPENAI_API_KEY be9bdecc8bf64e85bde69c04b2ad56f8
ENV OPENAI_API_HOST https://tiaa-openai-azure-sweden.openai.azure.com
ENV OPENAI_API_VERSION 2023-07-01-preview
ENV USER=pknadimp
ENV OPASSWORD=1234
ENV DATABASE=Money
ENV HOST=3.84.46.162


# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Make port 6060 available to the world outside this container
EXPOSE 6060

# Define environment variable
ENV FLASK_APP=challenge_generator.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=6060

# Run the application
CMD ["flask", "run"]
 