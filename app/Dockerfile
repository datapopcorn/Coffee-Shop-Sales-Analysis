FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++

RUN pip install -r requirements.txt

CMD ["echo", "Please use docker-compose command to run this container."]
