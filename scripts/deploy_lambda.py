import boto3
import os
from aws_service.aws_client import get_client

lambda_client = get_client("lambda")

# Read ZIP contents
with open("metrics_lambda/lambda.zip", "rb") as f:
    zipped_code = f.read()

# Deploy Lambda to LocalStack
response = lambda_client.create_function(
    FunctionName="logMetricsFunction",
    Runtime="python3.10",  # Match your Python version
    Role="arn:aws:iam::000000000000:role/lambda-role",  # LocalStack accepts dummy ARNs
    Handler="metrics_handler.lambda_handler",  # filename.function
    Code={"ZipFile": zipped_code},
    Publish=True
)

print("✅ Lambda created in LocalStack.")
print("Function ARN:", response["FunctionArn"])
