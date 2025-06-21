import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import json
import time
from aws_service.aws_client import get_client, get_resource

def verify_localstack_setup():
    """Verify LocalStack resources are properly created and working"""
    
    # Initialize clients
    dynamodb_client = get_client("dynamodb")
    
    dynamodb_resource = get_resource("dynamodb")
    
    s3_client = get_client("s3")

    print("🔍 Verifying LocalStack setup...")
    
    # Check DynamoDB tables
    try:
        tables = dynamodb_client.list_tables()
        print(f"📊 DynamoDB Tables: {tables['TableNames']}")
        
        for table_name in tables['TableNames']:
            try:
                table_info = dynamodb_client.describe_table(TableName=table_name)
                status = table_info['Table']['TableStatus']
                item_count = table_info['Table']['ItemCount']
                print(f"   - {table_name}: {status} (Items: {item_count})")
            except Exception as e:
                print(f"   - {table_name}: Error - {e}")
                
    except Exception as e:
        print(f"❌ Error checking DynamoDB: {e}")
    
    # Check S3 buckets
    try:
        buckets = s3_client.list_buckets()
        bucket_names = [b['Name'] for b in buckets['Buckets']]
        print(f"🪣 S3 Buckets: {bucket_names}")
    except Exception as e:
        print(f"❌ Error checking S3: {e}")

    # Test table operations with proper data types
    print("\n🧪 Testing table operations...")
    
    # Test 1: PDF_Metadata table
    try:
        table = dynamodb_resource.Table('PDF_Metadata')
        
        # Insert test data
        test_item = {
            'file_id': 'test-123',
            'filename': 'test.pdf',
            'uploaded_at': '2024-01-01T00:00:00'
        }
        
        table.put_item(Item=test_item)
        print("✅ PDF_Metadata: Insert successful")
        
        # Read test data
        response = table.get_item(Key={'file_id': 'test-123'})
        if 'Item' in response:
            print("✅ PDF_Metadata: Read successful")
            print(f"   Retrieved: {response['Item']}")
            # Cleanup
            table.delete_item(Key={'file_id': 'test-123'})
            print("✅ PDF_Metadata: Delete successful")
        else:
            print("❌ PDF_Metadata: Read failed")
            
    except Exception as e:
        print(f"❌ PDF_Metadata table test failed: {e}")

    # Test 2: QueryLog table
    try:
        table = dynamodb_resource.Table('QueryLog')
        
        test_item = {
            'run_id': 'test-run-123',
            'query_text': 'Test query',
            'response_text': 'Test response',
            'confidence_score': Decimal('0.85'),  # Using Decimal instead of float
            'file_id': 'test-file-456',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        table.put_item(Item=test_item)
        print("✅ QueryLog: Insert successful")
        
        response = table.get_item(Key={'run_id': 'test-run-123'})
        if 'Item' in response:
            print("✅ QueryLog: Read successful")
            print(f"   Retrieved: {response['Item']}")
            # Cleanup
            table.delete_item(Key={'run_id': 'test-run-123'})
            print("✅ QueryLog: Delete successful")
        else:
            print("❌ QueryLog: Read failed")
            
    except Exception as e:
        print(f"❌ QueryLog table test failed: {e}")

    # Test 3: LLM_Metrics table
    try:
        table = dynamodb_resource.Table('LLM_Metrics')
        
        test_item = {
            'run_id': 'test-metrics-123',
            'tokens_used': 150,
            'confidence_score': Decimal('0.92'),  # Using Decimal
            'response_time': Decimal('1.25'),     # Using Decimal
            'file_id': 'test-file-789'
        }
        
        table.put_item(Item=test_item)
        print("✅ LLM_Metrics: Insert successful")
        
        response = table.get_item(Key={'run_id': 'test-metrics-123'})
        if 'Item' in response:
            print("✅ LLM_Metrics: Read successful")
            print(f"   Retrieved: {response['Item']}")
            # Cleanup
            table.delete_item(Key={'run_id': 'test-metrics-123'})
            print("✅ LLM_Metrics: Delete successful")
        else:
            print("❌ LLM_Metrics: Read failed")
            
    except Exception as e:
        print(f"❌ LLM_Metrics table test failed: {e}")

    # Test 4: S3 operations
    try:
        bucket_name = 'pdf-storage-local'
        test_key = 'test-file.txt'
        test_content = b'This is a test file content'
        
        # Upload test
        s3_client.put_object(Bucket=bucket_name, Key=test_key, Body=test_content)
        print("✅ S3: Upload successful")
        
        # Download test
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read()
        
        if downloaded_content == test_content:
            print("✅ S3: Download successful")
        else:
            print("❌ S3: Download content mismatch")
            
        # Cleanup
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ S3: Delete successful")
        
    except Exception as e:
        print(f"❌ S3 test failed: {e}")

    # Test 5: Check current table contents
    print("\n📋 Current table contents:")
    
    for table_name in ['PDF_Metadata', 'QueryLog', 'LLM_Metrics']:
        try:
            table = dynamodb_resource.Table(table_name)
            response = table.scan(Limit=5)  # Get first 5 items
            items = response.get('Items', [])
            print(f"   {table_name}: {len(items)} items")
            
            if items:
                print(f"   Sample item: {items[0]}")
                
        except Exception as e:
            print(f"   ❌ Error scanning {table_name}: {e}")

    print("\n🎯 Verification complete!")
    print("\n💡 Tips for debugging:")
    print("   - Check LocalStack logs: docker logs localstack_main")
    print("   - Restart LocalStack if issues persist: docker-compose down && docker-compose up -d")
    print("   - Ensure all services use Decimal type for float values in DynamoDB")

def test_float_decimal_conversion():
    """Test float to decimal conversion specifically"""
    print("\n🔢 Testing float to Decimal conversion:")
    
    test_values = [
        0.85,
        1.23456789,
        0.0,
        1.0,
        99.99
    ]
    
    for val in test_values:
        decimal_val = Decimal(str(val))
        print(f"   {val} (float) -> {decimal_val} (Decimal) -> {float(decimal_val)} (back to float)")

if __name__ == "__main__":
    verify_localstack_setup()
    test_float_decimal_conversion()