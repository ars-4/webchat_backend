# Use an official Python runtime as a parent image
FROM python:3.7

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install django djangorestframework django-cors-headers django-filter pillow requests
RUN pip install -U channels[daphne]
RUN pip install channels_postgres

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run your application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "WebChat.asgi:application"]