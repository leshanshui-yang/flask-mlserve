FROM python:3.7.11-stretch

RUN pip install --upgrade pip
RUN pip install mlflow==1.20.2
RUN pip install numpy pandas torch
RUN pip install Flask flask-restplus Flask-SSLify Flask-Admin gunicorn
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl

COPY . /app
WORKDIR /app

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "serve"]
