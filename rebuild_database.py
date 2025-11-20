"""
Script to rebuild the vector database with correct embeddings
"""
import os
import shutil
from pathlib import Path
from app.services.ingestion import process_document
from app.services.database import get_supabase

def rebuild_database():
    print("🔄 Starting database rebuild...")
    
    # 1. Delete ChromaDB
    chroma_path = Path("data/chroma_db")
    if chroma_path.exists():
        print("🗑️  Deleting old ChromaDB...")
        shutil.rmtree(chroma_path)
        print("✅ ChromaDB deleted")
    
    # 2. Clear Supabase
    print("🗑️  Clearing Supabase tables...")
    supabase = get_supabase()
    try:
        supabase.table("chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Supabase cleared")
    except Exception as e:
        print(f"⚠️  Supabase clear warning: {e}")
    
    # 3. Re-process all documents
    data_dir = Path("data")
    txt_files = list(data_dir.glob("*.txt"))
    
    print(f"\n📚 Found {len(txt_files)} documents to process")
    
    for i, file_path in enumerate(txt_files, 1):
        print(f"\n[{i}/{len(txt_files)}] Processing: {file_path.name}")
        try:
            result = process_document(str(file_path))
            print(f"  ✅ Processed {result['total_chunks']} chunks")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n🎉 Database rebuild complete!")
    print("🔍 Test with: 'ما العلاقة بين اللغة والهوية الثقافية؟'")

if __name__ == "__main__":
    rebuild_database()
