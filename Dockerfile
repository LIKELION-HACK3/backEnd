FROM python:3.10.12

ENV PYTHONUNBUFFERED 1

#RUN apt-get -y update
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc pkg-config default-libmysqlclient-dev vim \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
ADD . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY .env .