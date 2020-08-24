"""Test Kafka Producer
"""
import os
import time
import json
from random import randint
from pykafka import KafkaClient
from pykafka.common import CompressionType

if __name__ == '__main__':
    kafka_broker = os.environ['KAFKA_BROKER']
    topic = os.getenv('KAFKA_TOPIC', 'test_kafka_topic')
    use_rdkafka = os.getenv('USE_RDKAFKA') is not None
    use_snappy = CompressionType.SNAPPY if os.getenv('USE_SNAPPY') is not None else 0

    client = KafkaClient(hosts=kafka_broker)
    topic = client.topics[topic]
    if use_rdkafka:
        print ("Using RDKafka")

    producer = topic.get_producer(
        sync=True,
        required_acks=0,
        use_rdkafka=use_rdkafka,
        compression=use_snappy
    )
    i = 0
    while True:
        key = 'k' + str(randint(1, 1000))
        msg = {'ts': round(1000*time.time()), 'id':key, 'value': randint(1, 1000)}
        i = i + 1
        producer.produce(json.dumps(msg).encode("utf-8"))
        if i%1000 == 1:
            print(i, "messages", json.dumps(msg))
