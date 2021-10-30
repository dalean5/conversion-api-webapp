import os

broker_host = os.environ["BROKER_HOST"]
broker_user = os.environ["BROKER_USER"]
broker_password = os.environ["BROKER_PASSWORD"]
broker_port = os.environ["BROKER_PORT"]
broker_vhost = os.environ["BROKER_VHOST"]


def get_broker_url() -> str:
    return "amqp://%s:%s@%s:%s/%s" % (
        broker_user,
        broker_password,
        broker_host,
        broker_port,
        broker_vhost,
    )
