from functools import lru_cache
import os
from pinecone import Pinecone

@lru_cache
def get_pinecone_index():
    api_key = os.environ.get("PINECONE_API_KEY")
    pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME")

    if not api_key or not pinecone_index_name:
        raise ValueError("Pinecone API key and index name must be set in environment variables.")
    pc = Pinecone(api_key=api_key)
    return pc.Index(pinecone_index_name)