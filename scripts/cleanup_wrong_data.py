"""
Script لحذف الـ chunks الخاطئة من Supabase
"""
import sys
import os

# إضافة project root إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.database import get_supabase

def delete_wrong_embeddings():
    """
    حذف الـ chunks التي تم نقلها بشكل خاطئ
    """
    print("="*70)
    print("🗑️  حذف البيانات الخاطئة من Supabase")
    print("="*70)
    
    supabase = get_supabase()
    
    # حذف كل الـ chunks التي لها embeddings
    # (نعرف أنها خاطئة لأن dimensions أكثر من 768)
    print("\n🔄 جاري حذف الـ chunks الخاطئة...")
    
    response = supabase.table("chunk").delete().not_.is_("embedding", "null").execute()
    
    deleted_count = len(response.data) if response.data else 0
    
    print(f"✅ تم حذف {deleted_count} chunks خاطئة")
    
    # التحقق
    check = supabase.rpc('check_migration_status').execute()
    
    if check.data:
        stats = check.data[0]
        print(f"\n📊 الحالة بعد الحذف:")
        print(f"   - إجمالي الصفوف: {stats['total_rows']}")
        print(f"   - الصفوف مع embeddings: {stats['rows_with_embeddings']}")
        print(f"   - النسبة: {stats['percentage']}%")
    
    print("\n✅ تم التنظيف بنجاح!")
    
    return True

if __name__ == "__main__":
    delete_wrong_embeddings()
