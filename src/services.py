import json
import io
import os
import logging
import uuid
from datetime import datetime, timedelta

import pandas as pd
from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions,
)
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy

logger = logging.getLogger(__name__)

conn_str = os.environ["AZ_STORAGE_CONN_STR"]
container_name = os.environ["AZ_STORAGE_CONTAINER_NAME"]
queue_name = os.environ["AZ_STORAGE_QUEUE_NAME"]
account_name = os.environ["AZ_STORAGE_ACCOUNT_NAME"]
account_key = os.environ["AZ_STORAGE_ACCOUNT_KEY"]


queue_client = QueueClient.from_connection_string(
    conn_str=conn_str, queue_name=queue_name
)
blob_service_client = BlobServiceClient.from_connection_string(conn_str=conn_str)


class ProcessCsvToJson:
    def __init__(self, buffer: io.BytesIO, email: str) -> None:
        self.file = buffer
        self.email = email

    def process(self) -> str:
        json_file = self._convert()
        blob_uri = self._upload_file(json_file)
        self._send_queue_message({"blob_uri": blob_uri})
        return blob_uri

    def _convert(self) -> io.BytesIO:
        buffer = io.BytesIO()
        try:
            df = pd.DataFrame(
                pd.read_csv(self.file, sep=",", header=0, index_col=False)
            )
            df.to_json(
                buffer,
                orient="records",
                date_format="epoch",
                double_precision=10,
                force_ascii=True,
                date_unit="ms",
                default_handler=None,
            )
        except Exception as e:
            logger.exception(e)
        return buffer

    def _upload_file(self, file: io.BytesIO) -> dict:
        blob_name = self._make_file_name()
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name,
        )

        try:
            blob_client.upload_blob(file.getvalue())
        except Exception as e:
            logger.exception(e)

        blob_uri = self._construct_blob_uri(blob_name)
        sas_token = self._generate_blob_sas_token(blob_name)
        return f"{blob_uri}?{sas_token}"

    def _send_queue_message(self, msg: dict):
        msg["email"] = self.email
        try:
            encoded_msg = BinaryBase64EncodePolicy().encode(
                json.dumps(msg).encode("utf-8")
            )
            queue_client.send_message(encoded_msg)
        except Exception as e:
            logger.exception(e)

    def _make_file_name(self) -> str:
        return f"{uuid.uuid4().hex}.json"

    def _construct_blob_uri(self, blob_name: str) -> str:
        return "https://%s.blob.core.windows.net/%s/%s" % (
            account_name,
            container_name,
            blob_name,
        )

    def _generate_blob_sas_token(self, blob_name: str):
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            account_key=account_key,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        print(sas_token)
        return sas_token
