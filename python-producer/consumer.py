"""[summary]
"""
import os
from pykafka import KafkaClient
from pykafka.common import OffsetType

if __name__ == '__main__':
    # logging.basicConfig(level='DEBUG')
    kafka_broker = os.environ['KAFKA_BROKER']
    client = KafkaClient(hosts=kafka_broker)
    topic = client.topics['ivan']
    consumer = topic.get_simple_consumer(
        consumer_group='IvanLocal',
        reset_offset_on_start=False,
        auto_offset_reset=OffsetType.LATEST,
        auto_commit_enable=True,
        auto_commit_interval_ms=1000,
        use_rdkafka=True,
        fetch_message_max_bytes=1024 * 10
    )

    i = 0
    for message in consumer:
        if message is not None:
            if message.value is not None:
                i = i + 1
                if i%5000 == 1:
                    print("Consumed messages", i)
