"""
Script للتحقق من البيانات المنقولة في Supabase
"""
import sys
import os

# إضافة project root إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.database import get_supabase

def check_migrated_data():
    """
    التحقق من البيانات المنقولة إلى Supabase
    """
    print("="*70)
    print("🔍 التحقق من البيانات المنقولة في Supabase")
    print("="*70)
    
    supabase = get_supabase()
    
    # استعلام لجلب الـ chunks التي لها embeddings
    print("\n📊 جلب الـ chunks التي تم نقلها...")
    
    response = supabase.table("chunk").select("*").not_.is_("embedding", "null").limit(10).execute()
    
    chunks = response.data
    
    print(f"\n✅ تم العثور على {len(chunks)} chunks منقولة")
    
    if len(chunks) == 0:
        print("\n⚠️ لم يتم العثور على أي chunks مع embeddings!")
        print("   تأكد من أن migration نجح")
        return False
    
    # عرض كل chunk
    print("\n" + "="*70)
    print("📄 محتوى الـ chunks المنقولة:")
    print("="*70)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n【 Chunk {i} 】")
        print(f"   ID: {chunk['id']}")
        print(f"   Document ID: {chunk['document_id']}")
        print(f"   Chunk Index: {chunk['chunk_index']}")
        print(f"   المحتوى: {chunk['content'][:150]}...")
        print(f"   Has Embedding: {'✅' if chunk['embedding'] else '❌'}")
        if chunk['embedding']:
            print(f"   Embedding Dimensions: {len(chunk['embedding'])}")
    
    print("\n" + "="*70)
    print("✅ التحقق اكتمل!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    check_migrated_data()
