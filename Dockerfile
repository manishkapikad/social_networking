FROM python:3.10

ENV PYTHONUNBUFFERED 1
COPY . /socialnetwork
WORKDIR /socialnetwork
RUN pip3 install -r requirements.txt
WORKDIR /socialnetwork