from functools import lru_cache
import os
from supabase import create_client, Client

@lru_cache
def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        raise ValueError("Supabase URL and secret key must be set in environment variables.")
    return create_client(url, key)