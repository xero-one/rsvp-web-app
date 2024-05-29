import boto3
from boto3.resources.base import ServiceResource
from config import DDB_Config
from args import env




def ddb() -> ServiceResource:
    endpoint_url = None if env == "production" else "http://localhost:8000"
    region_name = DDB_Config.DDB_REGION_NAME if env == "production" else "example"
    aws_access_key_id = DDB_Config.DDB_ACCESS_KEY_ID if env == "production" else "example"
    aws_secret_access_key = DDB_Config.DDB_SECRET_ACCESS_KEY if env == "production" else "example"

    ddb = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    return ddb

