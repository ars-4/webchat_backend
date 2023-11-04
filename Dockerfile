# Use an official Python runtime as a parent image
FROM python:3.7

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# RUN pip install virtualenv
# RUN virtualenv venv
# RUN source venv/bin/activate
RUN pip install django djangorestframework django-cors-headers django-filter pillow requests whitenoise
RUN pip install -U channels[daphne]
RUN pip install channels_postgres

RUN python manage.py migrate
# RUN python manage.py collectstatic
RUN python installation.py

# Make port 8000 available to the world outside this container
EXPOSE 8001

# Define the command to run your application
CMD ["daphne", "-b", "0.0.0.0", "-p", "8001", "WebChat.asgi:application"]