"""Test Kafka Producer
"""
import os
from datetime import datetime, timezone
import time
import json
from random import randint
from pykafka import KafkaClient
from pykafka.common import CompressionType

def produce_random(thekey: str, thespec: dict):
    if thespec.get(thekey).get("type") == "enum":
        vals = thespec.get(thekey).get("enum")
        r = randint(0, len(vals) - 1)
        return vals[r]

    return ""

if __name__ == '__main__':
    kafka_broker = os.environ['KAFKA_BROKER']
    topic = os.getenv('KAFKA_TOPIC', 'test_kafka_topic')
    use_rdkafka = os.getenv('USE_RDKAFKA') is not None
    use_snappy = CompressionType.SNAPPY if os.getenv('USE_SNAPPY') is not None else 0
    print_every = int(os.getenv('PRINT_EVERY', '1'))

    spec: dict = json.loads(os.environ['SPEC'])

    client = KafkaClient(hosts=kafka_broker)
    topic = client.topics[topic]

    if use_rdkafka:
        print("Using RDKafka")

    producer = topic.get_producer(
        sync=True,
        required_acks=0,
        use_rdkafka=use_rdkafka,
        compression=use_snappy
    )

    i = 0

    machine = spec.pop("machine")

    for key in spec:
        spec[key]["time"] = datetime.now(timezone.utc)

    while True:
        now = datetime.now(timezone.utc)

        for key in spec:
            before = spec.get(key).get('time', now)
            freq = spec.get(key).get("freq_seconds", 0)

            # only produce message if frequency has passed
            if (now-before).total_seconds() <= freq:
                continue

            spec[key]["time"] = now
            generated = produce_random(key, spec)

            msg = {"m":machine, "key":key, "value":generated, "ts":now.isoformat()}
            i = i + 1
            producer.produce(json.dumps(msg).encode("utf-8"))
            if i%print_every == 0:
                print(i, "messages", json.dumps(msg))

        time.sleep(1)
