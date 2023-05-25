import logging

import json
import pytest
import os

from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.types import TypeSerializer


def low_level_data_serialize(item):
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in item.items()}


def low_level_data_deserialize(item):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in item.items()}


@pytest.mark.asyncio
async def test_write_s3_bucket(s3_bucket):
    bucket = os.getenv("BUCKET")
    filename = "dummy.bin"
    folder = "test"
    key = f"{folder}/{filename}"
    data = b"\x01" * 1024
    response = await s3_bucket.put_object(Bucket=bucket, Key=key, Body=data)
    assert response.get('ResponseMetadata').get('HTTPStatusCode') == 200


@pytest.mark.asyncio
async def test_publish_sqs_package(sqs_queue):
    session, url_sqs = sqs_queue
    response = await session.send_message(
        QueueUrl=url_sqs, MessageBody=json.dumps({"test": "value"})
    )
    assert (
        response["MessageId"] and response["ResponseMetadata"]["HTTPStatusCode"] == 200
    )


@pytest.mark.asyncio
async def test_dynamo_batch_items(dynamodb_table, mock_event_dynamo):
    table_register_list = os.getenv("TABLE")
    response = await dynamodb_table.batch_write_item(
        RequestItems={
            table_register_list: [
                {"PutRequest": {"Item": low_level_data_serialize(item)}}
                for item in mock_event_dynamo
            ]
        }
    )
    assert len(response["UnprocessedItems"]) == 0
