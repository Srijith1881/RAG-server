import boto3
import os
from dotenv import load_dotenv
load_dotenv()

def get_client(service_name):
    use_local = os.getenv("USE_LOCALSTACK", "false").lower() == "true"
    kwargs = {
        "region_name": os.getenv("REGION"),
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY")
    }
    if use_local:
        kwargs["endpoint_url"] = "http://localhost:4566"
    return boto3.client(service_name, **kwargs)

def get_resource(service_name):
    use_local = os.getenv("USE_LOCALSTACK", "false").lower() == "true"
    kwargs = {
        "region_name": os.getenv("REGION"),
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY")
    }
    if use_local:
        kwargs["endpoint_url"] = "http://localhost:4566"
    return boto3.resource(service_name, **kwargs)



# def get_client(service_name):
#     kwargs = {
#         "region_name": os.getenv("REGION"),
#         "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
#         "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
#         "endpoint_url": os.getenv("ENDPOINT_URL", "http://localhost:4566")  # Always set
#     }
#     return boto3.client(service_name, **kwargs)

# def get_resource(service_name):
#     kwargs = {
#         "region_name": os.getenv("REGION"),
#         "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
#         "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
#         "endpoint_url": os.getenv("ENDPOINT_URL", "http://localhost:4566")  # Always set
#     }
#     return boto3.resource(service_name, **kwargs)

