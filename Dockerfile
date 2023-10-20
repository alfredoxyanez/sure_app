FROM python:3.9-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/