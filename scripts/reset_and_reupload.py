"""
Script لحذف البيانات الحالية وإعادة الرفع بالطريقة الصحيحة
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.database import get_supabase

def reset_and_reupload():
    print("="*70)
    print("🔄 حذف البيانات القديمة وإعادة الرفع")
    print("="*70)
    
    supabase = get_supabase()
    
    # حذف البيانات القديمة
    print("\n🗑️  حذف البيانات القديمة...")
    supabase.table("chunks_v2").delete().gte('id', 0).execute()
    supabase.table("documents_v2").delete().gte('id', 0).execute()
    
    print("✅ تم الحذف")
    
    # إعادة رفع المستند الاختباري
    print("\n📤 إعادة رفع المستند...")
    
    from app.services.ingestion import process_document
    
    test_file = "data/test_simple.txt"
    result = process_document(test_file)
    
    print(f"\n✅ تم رفع المستند:")
    print(f"   - Document ID: {result['document_id']}")
    print(f"   - Total chunks: {result['total_chunks']}")
    
    print("\n🔍 الآن جرب البحث:")
    print("   python scripts/test_search_v2.py")

if __name__ == "__main__":
    reset_and_reupload()
