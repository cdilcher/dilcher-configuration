# Below: fe Dockerfile
FROM python:3.8-alpine
ARG pypiuser
ARG pypipass
# Unit test before packaging
RUN mkdir -p /tmp/test/
COPY app/ /tmp/test/app/
COPY dilcher_configuration/ /tmp/test/dilcher_configuration/
COPY __init__.py /tmp/test/
COPY manage.py /tmp/test/
COPY requirements.txt /tmp/test/
WORKDIR /tmp/test
RUN pip install -r requirements.txt
RUN python manage.py test dilcher_configuration.tests
WORKDIR /tmp
RUN rm -rf /tmp/test
# Unit tests succeeded, start packaging the app
RUN python -m pip install --user --upgrade setuptools wheel
RUN mkdir -p /tmp/dilcher-configuration/dilcher_configuration
COPY dilcher_configuration/* /tmp/dilcher-configuration/dilcher_configuration/
COPY LICENSE /tmp/dilcher-configuration/
COPY Readme.md /tmp/dilcher-configuration/
COPY setup.py /tmp/dilcher-configuration/
COPY requirements.txt /tmp/dilcher-configuration/
WORKDIR /tmp/dilcher-configuration
RUN python setup.py sdist bdist_wheel
# App is packaged, publish it
COPY pypirc /tmp/
RUN sed -e "s/USERNAME/${pypiuser}/g; s/PASSWORD/${pypipass}/g;" /tmp/pypirc > /root/.pypirc
RUN apk update
RUN apk add --no-cache --virtual .build-deps build-base linux-headers python3-dev libffi libffi-dev py3-cffi libressl libressl-dev
RUN python -m pip install --user --upgrade twine
RUN python -m twine upload -r pypi dist/*