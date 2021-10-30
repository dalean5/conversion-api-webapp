import json
import logging
import os

from celery import Celery
from azure.storage.queue import QueueClient, BinaryBase64DecodePolicy

import config
from . import send_email

logger = logging.getLogger(__name__)


conn_str = os.environ["AZ_STORAGE_CONN_STR"]
queue_name = os.environ["AZ_STORAGE_QUEUE_NAME"]

app = Celery(__name__)
app.conf.update(
    broker_url=config.get_broker_url(),
    timezone="America/Jamaica",
    enable_utc=True,
)

queue_client = QueueClient.from_connection_string(
    conn_str=conn_str,
    queue_name=queue_name,
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        10.0, process_queue_messages.s(), name="process-queue-every-10-seconds"
    )

    sender.add_periodic_task(30.0, add_test.s(), expires=10)


@app.task(name="process_queue_messages")
def process_queue_messages():
    msgs = queue_client.receive_messages()
    for m in msgs:
        decoded_message = json.dumps(
            BinaryBase64DecodePolicy().decode(m.content)
        ).encode("utf-8")
        print(decoded_message)
    logger.info(f"processed {len(msgs)} messages")


@app.task(name="add_test")
def add_test():
    sum = 10 + 10
    print(sum)
