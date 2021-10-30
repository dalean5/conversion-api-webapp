import logging

logger = logging.getLogger(__name__)


def send_email(to: str, message: str):
    logger.info(f"Sending message: to - {to}, contents - {message}")
