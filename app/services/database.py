from supabase import create_client, Client
from app.core.config import settings

_supabase = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase

def insert_document_record(filename: str, total_chunks: int):
    supabase = get_supabase()
    data = {"filename": filename, "total_chunks": total_chunks}
    response = supabase.table("documents").insert(data).execute()
    return response.data[0]

def insert_chunks_records(chunks_data: list[dict]):
    supabase = get_supabase()
    response = supabase.table("chunk").insert(chunks_data).execute()
    return response.data
