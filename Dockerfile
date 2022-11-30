FROM python:3.7.11-stretch

RUN pip install --upgrade pip
RUN pip install mlflow==1.20.2
RUN pip install numpy pandas torch==1.7.1 torchvision==0.8.2 transformers==4.16.2 pyarrow
RUN pip install Flask flask-restplus Flask-SSLify Flask-Admin gunicorn
RUN pip install SQLAlchemy mysqlclient pyarrow psycopg2-binary==2.8.5 boto3
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl

RUN mkdir /mlflow/

COPY . /app
WORKDIR /app

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "serve"]
