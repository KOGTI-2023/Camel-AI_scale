# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========

import json

from confluent_kafka import Producer as ConfluentProducer  # type: ignore[import]


class Producer:
    r"""Kafka producer model using confluent_kafka"""

    def __init__(
        self, bootstrap_servers="localhost:9092", topic="default_topic", **kwargs
    ):
        r"""Initialize Confluent Kafka producer.

        Args:
            bootstrap_servers (str): Kafka broker(s) (default: :obj:`"localhost:9092"`).
            topic (str): Default topic to produce to (default: :obj:`"default_topic"`).
            **kwargs: Additional configuration parameters for confluent_kafka.Producer.
        """
        self.topic = topic
        config = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "python-producer",
        }
        config.update(kwargs)
        self.producer = ConfluentProducer(config)

    def delivery_report(self, err, msg):
        r"""Delivery report handler for produced messages.

        Args:
            err (confluent_kafka.KafkaError): Delivery error (if any)
            msg (confluent_kafka.Message): Delivered message
        """
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def produce(self, value, key=None, topic=None):
        r"""Produce a message to Kafka.

        Args:
            value: The message value that will be serialized to JSON format.
            key: Optional message key (default: :obj:`None`).
            topic: Optional topic override (default: :obj:`None`).
        """
        if topic is None:
            topic = self.topic

        try:
            value_json = json.dumps(value)
        except TypeError:
            raise ValueError("Value must be JSON serializable")

        self.producer.produce(
            topic, key=key, value=value_json, callback=self.delivery_report
        )
        # Serve delivery callback queue
        self.producer.poll(0)

    def flush(self):
        r"""Wait for any outstanding messages to be delivered."""
        self.producer.flush()

    def close(self):
        """Close the producer"""
        self.producer.flush()  # Make sure all outstanding messages are sent
