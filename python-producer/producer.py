"""[summary]
"""
import os
import time
import logging
import json
from random import randint
from pykafka import KafkaClient

if __name__ == '__main__':
    # logging.basicConfig(level='DEBUG')
    kafka_broker = os.environ['KAFKA_BROKER']
    client = KafkaClient(hosts=kafka_broker)
    topic = client.topics['ivan']
    producer = topic.get_producer(linger_ms=1000, sync=True)
    i = 0
    while True:
        msg = {'timestamp': time.time(), 'id:':i, 'value': randint(1, 1000)}
        i = i+1
        producer.produce(json.dumps(msg).encode("utf-8"))
        if i%1000 == 1:
            print(json.dumps(msg))
