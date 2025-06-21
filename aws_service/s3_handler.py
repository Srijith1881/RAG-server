# Handles S3 interactions

import boto3
import botocore
import os
from dotenv import load_dotenv
from aws_service.aws_client import get_client
from botocore.exceptions import ClientError

load_dotenv()

s3 = get_client("s3")

bucket = os.getenv("BUCKET_NAME")

def upload_to_s3(file_path, key):
    # Uploads a local file to the configured S3 bucket
    try:
        s3.upload_file(file_path, bucket, key)
    except ClientError as e:
        raise RuntimeError(f"Failed to upload to S3: {e}")

def download_from_s3(key, dest_path):
    # Downloads a file from S3 to the specified destination path.
    try:
        s3.download_file(bucket, key, dest_path)
    except ClientError as e:
        raise RuntimeError(f"Failed to download from S3: {e}")