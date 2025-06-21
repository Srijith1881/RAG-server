
# Handles interactions with the DynamoDB

import boto3
from datetime import datetime
import os
from decimal import Decimal
from dotenv import load_dotenv
from aws_service.aws_client import get_resource

load_dotenv()

dynamodb = get_resource("dynamodb")


table = dynamodb.Table("PDF_Metadata")

def convert_float_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_float_to_decimal(item) for item in obj]
    else:
        return obj

def save_metadata(file_id, filename):
    try:
        item = {
            "file_id": str(file_id),  # Ensure string
            "filename": str(filename),  # Ensure string
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Convert any potential float values to Decimal
        item = convert_float_to_decimal(item)
        
        table.put_item(Item=item)
        print(f"✅ Metadata saved successfully for file_id: {file_id}")
        
    except Exception as e:
        print(f"❌ Failed to save metadata to DynamoDB: {e}")
        print(f"Debug info - file_id: {file_id}, filename: {filename}")
        raise RuntimeError(f"Failed to save metadata to DynamoDB: {e}")

def get_metadata(file_id):
    try:
        response = table.get_item(Key={"file_id": str(file_id)})
        item = response.get("Item", {})
        
        # Convert Decimal back to float for JSON serialization if needed
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            else:
                return obj
        
        return decimal_to_float(item)
        
    except Exception as e:
        print(f"❌ Failed to get metadata: {e}")
        raise RuntimeError(f"Failed to get metadata: {e}")

def list_metadata():
    try:
        response = table.scan()
        items = response.get("Items", [])
        
        # Convert Decimal back to float for JSON serialization
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            else:
                return obj
        
        return [decimal_to_float(item) for item in items]
        
    except Exception as e:
        print(f"❌ Failed to list metadata: {e}")
        raise RuntimeError(f"Failed to list metadata: {e}")

def test_table_connection():
    """Test function to verify table connectivity"""
    try:
        response = table.describe_table()
        print(f"✅ Table {table.table_name} is accessible")
        print(f"Table status: {response['Table']['TableStatus']}")
        return True
    except Exception as e:
        print(f"❌ Table connection test failed: {e}")
        return False

# Test connection when module is imported
if __name__ == "__main__":
    test_table_connection()