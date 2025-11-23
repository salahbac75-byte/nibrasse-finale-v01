"""
Vector Store implementation using Supabase pgvector
يستبدل ChromaDB بـ Supabase pgvector للتوافق مع Vercel
"""
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from app.services.database import get_supabase
from typing import List, Dict, Any

def add_documents_to_supabase(
    ids: List[str],
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    embeddings: List[List[float]]
):
    """
    إضافة documents مع embeddings إلى Supabase
    
    Args:
        ids: قائمة IDs (embedding_id)
        documents: قائمة النصوص
        metadatas: قائمة metadata (تحتوي على document_id, chunk_index, filename)
        embeddings: قائمة vectors (768 dimension)
    """
    supabase = get_supabase()
    
    # تحضير البيانات للإدراج
    chunks_data = []
    for i in range(len(ids)):
        # تحويل embedding لـ list إذا كان numpy array
        embedding = embeddings[i]
        if hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()
        
        # ✅ للتخزين: نرسل list مباشرة (Supabase يحولها لـ vector تلقائياً)
        # ⚠️ للبحث: نرسل text (RPC يحولها صراحةً بـ ::vector)
        
        chunk_data = {
            "document_id": metadatas[i].get("document_id"),
            "chunk_index": metadatas[i].get("chunk_index"),
            "content": documents[i],
            "embedding_id": ids[i],
            "embedding": embedding  # ✅ list مباشرة للتخزين
        }
        chunks_data.append(chunk_data)
    
    # طباعة debug info لأول chunk
    if len(chunks_data) > 0:
        test_emb = chunks_data[0]['embedding']
        print(f"📊 Debug - Embedding info:")
        print(f"   - Type: {type(test_emb)}")
        print(f"   - Length: {len(test_emb)}")
        if len(test_emb) > 0:
            print(f"   - First element type: {type(test_emb[0])}")
    
    # إدراج في Supabase (batch) - استخدام الجدول الجديد
    response = supabase.table("chunks_v2").insert(chunks_data).execute()  # ✅ v2
    
    print(f"✅ تم إضافة {len(chunks_data)} chunks إلى Supabase pgvector (v2)")
    
    return response.data


def query_supabase_vectors(
    query_embedding: List[float],
    n_results: int = 20,
    filter_document_id: int = None
) -> Dict[str, Any]:
    """
    البحث الفيكتوري في Supabase باستخدام PostgreSQL مباشرة
    
    Args:
        query_embedding: vector الاستعلام (768 dimension)
        n_results: عدد النتائج المطلوبة
        filter_document_id: تصفية حسب document_id (اختياري)
    
    Returns:
        نتائج بنفس شكل ChromaDB
    """
    # التأكد من أن query_embedding هو list
    if hasattr(query_embedding, 'tolist'):
        query_embedding = query_embedding.tolist()
    
    # الحصول على Database URL من .env
    db_url = os.getenv('SUPABASE_DB_URL')
    
    if not db_url:
        print("❌ Error: SUPABASE_DB_URL not found in .env")
        return {"ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]}
    
    try:
        # الاتصال بـ PostgreSQL مباشرة
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # تحويل embedding لـ PostgreSQL array format
        embedding_str = '[' + ','.join([str(x) for x in query_embedding]) + ']'
        
        print(f"🔍 Debug:")
        print(f"   - embedding_str[:100]: {embedding_str[:100]}")
        
        # التحقق من database و schema
        cursor.execute("SELECT current_database(), current_schema()")
        db_info = cursor.fetchone()
        print(f"   - Current DB: {db_info}")
        
        # التحقق من وجود الجدول
        cursor.execute("SELECT COUNT(*) FROM chunks_v2")
        count = cursor.fetchone()
        print(f"   - Total rows in chunks_v2: {count}")
        
        # SQL query مع embedding مباشرة
        query = f"""
            SELECT
                id,
                document_id,
                chunk_index,
                content,
                embedding_id,
                1 - (embedding <=> '{embedding_str}'::vector) as similarity
            FROM chunks_v2
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT {n_results}
        """
        
        print(f"   - Query first 200 chars: {query[:200]}")
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"   - Raw results count: {len(results)}")
        if results:
            print(f"   - First result: {results[0]}")
        
        cursor.close()
        conn.close()
        
        print(f"✅ PostgreSQL direct: found {len(results)} results")
        
        # تحويل النتيجة لنفس شكل ChromaDB
        documents = []
        ids = []
        metadatas = []
        distances = []
        
        for row in results:
            documents.append(row['content'])
            ids.append(str(row['id']))
            metadatas.append({
                "document_id": row['document_id'],
                "chunk_index": row['chunk_index'],
                "embedding_id": row['embedding_id']
            })
            distances.append(row['similarity'])
        
        return {
            "ids": [ids],
            "distances": [distances],
            "metadatas": [metadatas],
            "documents": [documents]
        }
        
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")
        import traceback
        traceback.print_exc()
        return {"ids": [[]], "distances": [[]], "metadatas": [[]], "documents": [[]]}


def get_collection_count() -> int:
    """
    الحصول على عدد الـ chunks في Supabase v2
    """
    supabase = get_supabase()
    result = supabase.rpc('check_migration_status_v2').execute()  # ✅ v2
    
    if result.data and len(result.data) > 0:
        return result.data[0]['total_rows']
    
    return 0


def delete_collection():
    """
    حذف جميع الـ chunks من v2 (للاختبار فقط)
    ⚠️ استخدم بحذر!
    """
    supabase = get_supabase()
    supabase.table("chunks_v2").delete().neq('id', 0).execute()  # ✅ v2
    print("⚠️ تم حذف جميع الـ chunks من Supabase v2")
