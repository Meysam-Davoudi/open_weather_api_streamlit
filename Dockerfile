FROM python:3.11.9-slim

WORKDIR app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ARG PG_DBNAME='open_weather'
ARG PG_USER='root'
ARG PG_PASSWORD='123456'
ARG PG_HOST='localhost'
ARG PG_PORT='5432'

ENV PG_DBNAME=${PG_DBNAME} \
    PG_USER=${PG_USER} \
    PG_HOST=${PG_HOST} \
    PG_HOST=${PG_HOST} \
    PG_PORT=${PG_PORT}


EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "main.py"]