#!/usr/bin/env python3
"""
Simple test script to debug Supabase connection
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

print("=== Supabase Connection Test ===")
print(f"URL: {SUPABASE_URL}")
print(f"Service Key: {SUPABASE_SERVICE_KEY[:20]}..." if SUPABASE_SERVICE_KEY else "❌ Service Key Missing")

try:
    print("\n1. Testing import...")
    from supabase import create_client
    print("✅ Supabase import successful")
    
    print("\n2. Testing client creation...")
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Supabase client created")
    
    print("\n3. Testing connection...")
    # Simple test query
    result = supabase.table('users').select('count').execute()
    print("✅ Database connection successful!")
    print(f"Response: {result}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"Error type: {type(e)}")
    
    # More detailed error info
    import traceback
    traceback.print_exc()
