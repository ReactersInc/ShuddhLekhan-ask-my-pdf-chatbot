"""
Supabase Admin Client for Server-Side Operations
This client uses the SERVICE_ROLE key to bypass RLS for server operations
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is required in environment variables")

if not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_SERVICE_KEY is required in environment variables")

try:
    # Initialize Supabase admin client - use simple initialization
    supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print(f"✅ Supabase Admin Client initialized for: {SUPABASE_URL}")
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {str(e)}")
    # Create a dummy client to prevent import errors
    supabase_admin = None
