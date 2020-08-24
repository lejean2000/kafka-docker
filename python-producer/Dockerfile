FROM python:rc-alpine

COPY producer.py /tmp/

RUN apk add --no-cache musl-dev gcc g++ git librdkafka-dev snappy-dev \
&& cd /tmp && git clone https://github.com/Parsely/pykafka.git \
&& cd pykafka && python setup.py develop \
&& python -m pip install python-snappy

ENTRYPOINT ["/usr/local/bin/python", "/tmp/producer.py"]
