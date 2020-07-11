FROM library/python:3.7-slim

ENV PYTHONDONTWRITEBYTECODE=True

RUN mkdir -p /usr/app
WORKDIR /usr/app

COPY requirements.txt /usr/app
COPY dist/graph-*.whl /usr/app

RUN pip3.7 install -r requirements.txt
RUN pip3.7 install graph-*.whl

ADD . /usr/app

EXPOSE 8080

CMD aio-api-setup-schemas & aio-api-app
