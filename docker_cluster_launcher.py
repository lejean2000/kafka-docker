"""Generate Kafka cluster docker compose file"""
import sys
# from collections import OrderedDict
import ruamel.yaml

def ys(x):
    return ruamel.yaml.scalarstring.DoubleQuotedScalarString(x)


class KafkaBrokerDef:
    """Defines the docker compose section for a broker"""

    def __init__(self, broker_id: int, numzoos: int):
        self.numzoos = numzoos
        self.broker_id = broker_id
        self.name = 'broker'+str(broker_id)
        self.port = str(29000 + broker_id)
        self.name_port = self.name + ":" + self.port
        self.jmx_port = str(9000 + broker_id)
        self.definition = {}

    def generate(self) -> dict:
        self.definition['image'] = ys('farrider/kafka')
        self.definition['hostname'] = self.name
        self.definition['container_name'] = self.name
        self.definition['restart'] = 'unless-stopped'
        self.definition['ports'] = [self.port+":"+self.port, self.jmx_port+":"+self.jmx_port]

        environment = {}
        environment['KAFKA_BROKER_ID'] = 10+self.broker_id
        environment['KAFKA_ZOOKEEPER_CONNECT'] = ys(ZooDef.get_kafka_string(self.numzoos))
        environment['KAFKA_LISTENER_SECURITY_PROTOCOL_MAP'] = 'PLAINTEXT:PLAINTEXT'
        environment['KAFKA_ADVERTISED_LISTENERS'] = 'PLAINTEXT://${URL}:' + self.port
        environment['KAFKA_LISTENERS'] = 'PLAINTEXT://' + self.name_port
        environment['KAFKA_AUTO_CREATE_TOPICS_ENABLE'] = 'true'
        environment['KAFKA_NUM_PARTITIONS'] = 3
        environment['KAFKA_DEFAULT_REPLICATION_FACTOR'] = 2
        environment['KAFKA_JMX_HOSTNAME'] = self.name
        environment['KAFKA_JVM_PERFORMANCE_OPTS'] = ys("-XX:+UnlockExperimentalVMOptions -XX:+UseZGC -XX:SoftMaxHeapSize=2G")
        environment['KAFKA_HEAP_OPTS'] = '-Xms1g -Xmx5g'
        environment['KAFKA_JMX_PORT'] = self.jmx_port
        environment['KAFKA_JMX_OPTS'] = "-Djava.rmi.server.hostname={} ".format(self.name)
        environment['KAFKA_JMX_OPTS'] += "-Dcom.sun.management.jmxremote.local.only=false "
        environment['KAFKA_JMX_OPTS'] += "-Dcom.sun.management.jmxremote.rmi.port={} ".format(self.jmx_port)
        environment['KAFKA_JMX_OPTS'] += "-Dcom.sun.management.jmxremote.port={} ".format(self.jmx_port)
        environment['KAFKA_JMX_OPTS'] += "-Dcom.sun.management.jmxremote.authenticate=false "
        environment['KAFKA_JMX_OPTS'] += "-Dcom.sun.management.jmxremote.ssl=false"

        environment['KAFKA_JMX_OPTS'] = ys(environment['KAFKA_JMX_OPTS'])

        self.definition['environment'] = environment
        return self.definition


class ZooDef:
    """Defines the docker compose section for a zookeeper"""

    def __init__(self, zoo_id: int, numzoos: int):
        self.numzoos = numzoos
        self.zoo_id = zoo_id
        self.name = ZooDef.get_name(zoo_id)
        self.port = 2181
        self.name_port = ZooDef.get_name_port(zoo_id)
        self.definition = {}

    @staticmethod
    def get_name(zoo_id: int):
        return 'zoo'+str(zoo_id)

    @staticmethod
    def get_name_port(zoo_id: int):
        return ZooDef.get_name(zoo_id) + ':2181'

    @staticmethod
    def get_kafka_string(numzoos: int):
        kfkstrings = [ZooDef.get_name_port(n) for n in range(1, 1+numzoos)]
        return ",".join(kfkstrings)

    @staticmethod
    def get_zoo_string_single(zoo_id: int):
        return ZooDef.get_name(zoo_id) + ':2181'

    @staticmethod
    def get_zoo_string(numzoos: int):
        zoostrings = [ZooDef.get_zoo_string_single(n) for n in range(1, 1+numzoos)]
        return ",".join(zoostrings)        

    def generate(self) -> dict:
        self.definition['image'] = ys('zookeeper:latest')
        self.definition['container_name'] = self.name
        self.definition['hostname'] = self.name

        environment = {}
        environment['ZOOKEEPER_SERVER_ID'] = self.zoo_id
        environment['ZOOKEEPER_CLIENT_PORT'] = self.port
        environment['ZOOKEEPER_TICK_TIME'] = 2000
        environment['ZOOKEEPER_INIT_LIMIT'] = 5
        environment['ZOOKEEPER_SYNC_LIMIT'] = 2
        environment['ZOOKEEPER_SERVERS'] = ys(ZooDef.get_zoo_string(self.numzoos))

        self.definition['environment'] = environment
        return self.definition


numkakfka = int(sys.argv[1])
numzoo = int(sys.argv[2])

definition = {}
definition['version'] = '3.6'
services = {}

for i in range(1, 1+numzoo):
    z = ZooDef(i, numzoo)
    services[z.name] = z.generate()

for i in range(1, 1+numkakfka):
    k = KafkaBrokerDef(i, numzoo)
    services[k.name] = k.generate()

definition['services'] = services

ruamel.yaml.round_trip_dump(definition, sys.stdout, explicit_start=True)
