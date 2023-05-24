import json
import logging
import os
from uuid import uuid4

import pytest
from aiobotocore.session import get_session
from moto.dynamodb.exceptions import ResourceInUseException

from .mock_server import start_service
from .mock_server import stop_process


class MockContext(object):
    def __init__(self, function_name):
        self.function_name = function_name
        self.function_version = "v%LASTEST"
        self.memory_limit_in_mb = "128"
        self.invoked_function_arn = f"arn:lambda:{os.getenv('AWS_REGION_NAME')}:ACCOUNT:function:{self.function_name}"
        self.aws_request_id = uuid4.__str__


@pytest.fixture
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION_NAME"] = "us-east-1"


@pytest.fixture(scope="function")
def dynamodb_server():
    host = "localhost"
    port = 5001
    url = "http://{host}:{port}".format(host=host, port=port)
    process = start_service("dynamodb", host, port)
    yield url
    stop_process(process)


@pytest.fixture(scope="function")
def sqs_server():
    host = "localhost"
    port = 5002
    url = "http://{host}:{port}".format(host=host, port=port)
    process = start_service("sqs", host, port)
    yield url
    stop_process(process)


@pytest.fixture(scope="function")
def s3_server():
    host = "localhost"
    port = 5003
    url = "http://{host}:{port}".format(host=host, port=port)
    process = start_service("s3", host, port)
    yield url
    stop_process(process)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def dynamo_client(aws_credentials, dynamodb_server):
    session = get_session()
    async with session.create_client(
        "dynamodb", region_name="us-east-1", endpoint_url=dynamodb_server
    ) as client:
        yield client


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def sqs_client(aws_credentials, sqs_server):
    session = get_session()
    async with session.create_client(
        "sqs", region_name="us-east-1", endpoint_url=sqs_server
    ) as client:
        yield client


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def s3_client(aws_credentials, s3_server):
    session = get_session()
    async with session.create_client(
        "s3", region_name="us-east-1", endpoint_url=s3_server
    ) as client:
        yield client


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def dynamodb_table(dynamo_client, monkeypatch):
    TABLE_NAME = "TB_MOCK"
    logging.info("Requesting table creation...")
    try:
        await dynamo_client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        waiter = dynamo_client.get_waiter("table_exists")
        await waiter.wait(TableName=TABLE_NAME)
        logging.info(f"Table {TABLE_NAME} created")
        monkeypatch.setenv("TABLE", TABLE_NAME)
        yield dynamo_client

    except ResourceInUseException:
        pass


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def sqs_queue(sqs_client, monkeypatch):
    QUEUE_NAME = "SQS_TEST"
    try:
        response = await sqs_client.create_queue(QueueName=QUEUE_NAME)
        queue_url = response["QueueUrl"]
        logging.info(f"SQS {QUEUE_NAME} created")
        monkeypatch.setenv("SQS_URL_PUBLISH", queue_url)
        yield sqs_client, queue_url
    except ResourceInUseException:
        pass


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def s3_bucket(s3_client, monkeypatch):
    BUCKET_NAME = "BUCKET_TEST"
    try:
        await s3_client.create_bucket(Bucket=BUCKET_NAME)
        monkeypatch.setenv("BUCKET", BUCKET_NAME)
        yield s3_client
    except ResourceInUseException:
        pass


@pytest.fixture
def mock_event_sqs():
    with open("events/package_sqs.json", "r", encoding="utf8") as fp:
        return json.load(fp)


@pytest.fixture
def mock_event_dynamo():
    with open("events/package_dynamo.json", "r", encoding="utf8") as fp:
        return json.load(fp)
