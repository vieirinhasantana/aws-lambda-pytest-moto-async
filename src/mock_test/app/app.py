import asyncio
import json
import os

from functools import reduce
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.types import TypeSerializer
from .session import Session

logger = Logger()

def low_level_data_serialize(item):
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in item.items()}

async def insert_batch_dynamo(client, items: list):
    try:
        table_register_equities = os.getenv("TB_REGISTER_ACOES")
        return await client.batch_write_item(
            RequestItems={
                table_register_equities: [
                    {"PutRequest": {"Item": low_level_data_serialize(item)}}
                    for item in items
                ]
            }
        )

    except Exception as e:
        logger.exception("Received a DYNAMO error")
        raise RuntimeError("Unable to fullfil request") from e


async def handler(event: dict) -> None:
    pass


@logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> None:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event))
