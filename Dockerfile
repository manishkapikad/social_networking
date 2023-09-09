FROM python:3.10

ENV PYTHONUNBUFFERED 1

COPY . /socialnetwork

# Set up the Django settings to use MariaDB
WORKDIR /socialnetwork

# Install Django and other Python dependencies
RUN pip3 install -r requirements.txt

WORKDIR /socialnetwork