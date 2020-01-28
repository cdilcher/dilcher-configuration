# Below: fe Dockerfile
FROM python:3.8-alpine
ARG pypiuser
ARG pypipass
# Unit test before packaging
RUN mkdir -p /tmp/test/app
COPY app/* /tmp/test/app/
RUN mkdir -p /tmp/test/dilcher_configuration
COPY dilcher_configuration/* /tmp/test/dilcher_configuration/
COPY __init__.py /tmp/test/
COPY manage.py /tmp/test/
COPY requirements.txt /tmp/test/
WORKDIR /tmp/test
RUN pip install -r requirements.txt
RUN python manage.py test
