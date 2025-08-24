FROM python:3.10.12

ENV PYTHONUNBUFFERED 1

#RUN apt-get -y update
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc pkg-config default-libmysqlclient-dev libpq-dev \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get -y install vim

RUN mkdir /app
ADD . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY .env .