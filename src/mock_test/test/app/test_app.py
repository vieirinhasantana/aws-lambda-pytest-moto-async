import json
import logging
import pytest

from datetime import datetime
from functools import reduce
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.types import TypeSerializer


def low_level_data_serialize(item):
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in item.items()}


def low_level_data_deserialize(item):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in item.items()}


@pytest.fixture
def load_mock_items(mock_all_register) -> list:
    payload = list()

    for item in mock_all_register.get("pageProps").get("rawList"):
        payload.append(
            {
                "ticker": item.get("ticker").upper(),
                "code_cvm": item.get("code_cvm"),
                "companyName": item.get("company_name"),
                "isin": item.get("isin"),
                "createdAt": datetime.now().isoformat(),
            }
        )

    return payload

@pytest.mark.asyncio
async def test_publish_sqs_package(sqs_queue_register_detail):
    session, url_sqs = sqs_queue_register_detail
    response = await session.send_message(
        QueueUrl=url_sqs, MessageBody=json.dumps({"test": "value"})
    )
    logging.info(response)
    assert (
        response["MessageId"] and response["ResponseMetadata"]["HTTPStatusCode"] == 200
    )

@pytest.mark.asyncio
async def test_publish_package_sqs_batch(sqs_queue_register_detail, mock_all_register):
    all_tickers = mock_all_register.get("pageProps").get("rawList")
    session, _ = sqs_queue_register_detail
    response = await publish_package_sqs_batch(all_tickers, session)
    assert response

@pytest.mark.asyncio
async def test_publish_package_sqs_batch_empty(sqs_queue_register_detail):
    session, _ = sqs_queue_register_detail
    result = await publish_package_sqs_batch([], session)
    assert result

@pytest.mark.asyncio
async def test_publish_package_sqs_batch_exception():
    with pytest.raises(RuntimeError, match="Unable to fullfil request"):
        await publish_package_sqs_batch(None, [{"test": "value"}])
