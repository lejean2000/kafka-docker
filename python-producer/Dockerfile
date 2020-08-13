FROM python:rc-alpine

COPY producer.py /tmp/

RUN python -m pip install pykafka

ENTRYPOINT ["/usr/local/bin/python", "/tmp/producer.py"]