# Below: fe Dockerfile
FROM python:3.8-alpine
ARG pypiuser
ARG pypipass
# Unit test before packaging
RUN mkdir -p /tmp/test/
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
ADD . /tmp/test
WORKDIR /tmp/test
RUN mkdir -p /tmp/test/test-reports/flake8
RUN mkdir -p /tmp/test/test-reports/unittest
RUN mkdir -p /tmp/test/test-reports/coverage
RUN flake8 --output-file=/tmp/test/test-reports/flake8/flake8.txt --tee --exit-zero . 2>&1
RUN flake8_junit /tmp/test/test-reports/flake8/flake8.txt /tmp/test/test-reports/flake8/flake8_junit.xml
RUN coverage run --source="." manage.py test dilcher_configuration.tests
RUN coverage report
RUN coverage xml
RUN mv /tmp/test/coverage.xml /tmp/test/test-reports/coverage/coverage.xml
CMD ["sleep", "300"]