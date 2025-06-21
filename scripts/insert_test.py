import boto3
from decimal import Decimal
from datetime import datetime
import json
from aws_service.aws_client import get_resource

def test_direct_inserts():
    """Test direct insertions to identify the exact issue"""
    
    # Initialize DynamoDB resource
    dynamodb = get_resource("dynamodb")

    print("🧪 Testing direct insertions to DynamoDB tables...")

    # Test 1: Simple QueryLog insertion
    print("\n1️⃣ Testing QueryLog table...")
    try:
        table = dynamodb.Table('QueryLog')
        
        # Simple test item with all required fields
        simple_item = {
            'run_id': 'debug-test-001',
            'query_text': 'What is the capital of France?',
            'response_text': 'The capital of France is Paris.',
            'confidence_score': Decimal('0.95'),  # Using Decimal explicitly
            'file_id': 'test-file-001',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"Inserting item: {simple_item}")
        table.put_item(Item=simple_item)
        print("✅ QueryLog insertion successful!")
        
        # Verify insertion
        response = table.get_item(Key={'run_id': 'debug-test-001'})
        if 'Item' in response:
            print(f"✅ QueryLog retrieval successful: {response['Item']}")
        else:
            print("❌ QueryLog retrieval failed")
            
    except Exception as e:
        print(f"❌ QueryLog test failed: {e}")
        print(f"Error type: {type(e)}")

    # Test 2: LLM_Metrics insertion
    print("\n2️⃣ Testing LLM_Metrics table...")
    try:
        table = dynamodb.Table('LLM_Metrics')
        
        metrics_item = {
            'run_id': 'debug-metrics-001',
            'tokens_used': 150,
            'confidence_score': Decimal('0.87'),
            'response_time': Decimal('2.34'),
            'file_id': 'test-file-metrics-001'
        }
        
        print(f"Inserting metrics: {metrics_item}")
        table.put_item(Item=metrics_item)
        print("✅ LLM_Metrics insertion successful!")
        
        # Verify insertion
        response = table.get_item(Key={'run_id': 'debug-metrics-001'})
        if 'Item' in response:
            print(f"✅ LLM_Metrics retrieval successful: {response['Item']}")
        else:
            print("❌ LLM_Metrics retrieval failed")
            
    except Exception as e:
        print(f"❌ LLM_Metrics test failed: {e}")
        print(f"Error type: {type(e)}")

    # Test 3: PDF_Metadata insertion
    print("\n3️⃣ Testing PDF_Metadata table...")
    try:
        table = dynamodb.Table('PDF_Metadata')
        
        pdf_item = {
            'file_id': 'debug-pdf-001',
            'filename': 'test-document.pdf',
            'uploaded_at': datetime.utcnow().isoformat()
        }
        
        print(f"Inserting PDF metadata: {pdf_item}")
        table.put_item(Item=pdf_item)
        print("✅ PDF_Metadata insertion successful!")
        
        # Verify insertion
        response = table.get_item(Key={'file_id': 'debug-pdf-001'})
        if 'Item' in response:
            print(f"✅ PDF_Metadata retrieval successful: {response['Item']}")
        else:
            print("❌ PDF_Metadata retrieval failed")
            
    except Exception as e:
        print(f"❌ PDF_Metadata test failed: {e}")
        print(f"Error type: {type(e)}")

    # Test 4: Check all tables after insertions
    print("\n4️⃣ Checking all tables after insertions...")
    
    tables_to_check = ['QueryLog', 'LLM_Metrics', 'PDF_Metadata']
    
    for table_name in tables_to_check:
        try:
            table = dynamodb.Table(table_name)
            response = table.scan()
            items = response.get('Items', [])
            print(f"📊 {table_name}: {len(items)} total items")
            
            if items:
                print(f"   Latest item: {items[-1]}")
            else:
                print("   ⚠️ No items found")
                
        except Exception as e:
            print(f"❌ Error scanning {table_name}: {e}")

def test_problematic_data_types():
    """Test different data types that might cause issues"""
    
    print("\n🔍 Testing problematic data types...")
    
    # Test different number types
    test_cases = [
        ("Regular float", 0.85),
        ("Integer", 100),
        ("String number", "0.85"),
        ("Decimal", Decimal('0.85')),
        ("Large float", 123.456789012345),
        ("Very small float", 0.000001),
        ("Zero", 0.0),
        ("Negative", -0.5)
    ]
    
    dynamodb = get_resource("dynamodb")
    
    table = dynamodb.Table('QueryLog')
    
    for description, value in test_cases:
        try:
            # Convert to Decimal if it's a number
            if isinstance(value, (int, float)):
                confidence_score = Decimal(str(value))
            else:
                confidence_score = value
                
            test_item = {
                'run_id': f'type-test-{test_cases.index((description, value))}',
                'query_text': f'Test query for {description}',
                'response_text': f'Test response for {description}',
                'confidence_score': confidence_score,
                'file_id': 'type-test-file',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            table.put_item(Item=test_item)
            print(f"✅ {description}: {value} -> SUCCESS")
            
        except Exception as e:
            print(f"❌ {description}: {value} -> FAILED: {e}")

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    dynamodb = get_resource("dynamodb")
    
    # Clean QueryLog
    try:
        table = dynamodb.Table('QueryLog')
        
        # Delete debug items
        debug_items = [
            'debug-test-001',
            'type-test-0', 'type-test-1', 'type-test-2', 'type-test-3',
            'type-test-4', 'type-test-5', 'type-test-6', 'type-test-7'
        ]
        
        for run_id in debug_items:
            try:
                table.delete_item(Key={'run_id': run_id})
                print(f"🗑️ Deleted QueryLog item: {run_id}")
            except:
                pass  # Item might not exist
                
    except Exception as e:
        print(f"❌ Error cleaning QueryLog: {e}")
    
    # Clean LLM_Metrics
    try:
        table = dynamodb.Table('LLM_Metrics')
        table.delete_item(Key={'run_id': 'debug-metrics-001'})
        print("🗑️ Deleted LLM_Metrics test item")
    except:
        pass
    
    # Clean PDF_Metadata
    try:
        table = dynamodb.Table('PDF_Metadata')
        table.delete_item(Key={'file_id': 'debug-pdf-001'})
        print("🗑️ Deleted PDF_Metadata test item")
    except:
        pass

if __name__ == "__main__":
    print("🚀 Starting comprehensive DynamoDB debug test...")
    
    test_direct_inserts()
    test_problematic_data_types()
    
    input("\nPress Enter to clean up test data...")
    cleanup_test_data()
    
    print("\n✅ Debug test complete!")