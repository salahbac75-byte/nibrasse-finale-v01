from fastapi import APIRouter, UploadFile, File, Body
from app.services.ingestion import save_uploaded_file, process_document
from app.services.rag import rag_pipeline
from app.services.database import get_supabase

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = save_uploaded_file(file)
    result = process_document(file_path)
    return {"message": "File processed successfully", "data": result}

@router.get("/documents")
async def get_documents():
    """Get list of all uploaded documents"""
    supabase = get_supabase()
    response = supabase.table("documents").select("*").order("upload_date", desc=True).execute()
    return {"documents": response.data}

@router.post("/query")
async def query_rag(query: str = Body(..., embed=True)):
    result = rag_pipeline(query)
    return result
