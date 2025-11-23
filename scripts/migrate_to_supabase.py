"""
Script لنقل البيانات من ChromaDB (backup) إلى Supabase pgvector
"""
import pickle
import sys
import os

# إضافة project root إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.vector_store_supabase import add_documents_to_supabase
from app.services.database import get_supabase

def migrate_chromadb_to_supabase(backup_file: str, test_mode: bool = True):
    """
    نقل البيانات من ChromaDB backup إلى Supabase
    
    Args:
        backup_file: مسار ملف النسخة الاحتياطية (.pkl)
        test_mode: إذا True، ينقل 5 chunks فقط للاختبار
    """
    print("🔄 جاري قراءة النسخة الاحتياطية...")
    
    # قراءة backup
    try:
        with open(backup_file, 'rb') as f:
            backup_data = pickle.load(f)
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")
        return False
    
    data = backup_data['data']
    total_chunks = len(data['ids'])
    
    print(f"📊 تم تحميل {total_chunks} chunks من النسخة الاحتياطية")
    print(f"📅 تاريخ التصدير: {backup_data['export_date']}")
    
    # تحديد عدد الـ chunks للنقل
    if test_mode:
        chunk_count = min(5, total_chunks)
        print(f"\n⚠️ وضع الاختبار: سيتم نقل {chunk_count} chunks فقط")
    else:
        chunk_count = total_chunks
        print(f"\n🚀 وضع الإنتاج: سيتم نقل جميع الـ {chunk_count} chunks")
    
    # استخراج البيانات
    ids = data['ids'][:chunk_count]
    embeddings = data['embeddings'][:chunk_count]
    documents = data['documents'][:chunk_count]
    metadatas = data['metadatas'][:chunk_count]
    
    print("\n🔄 جاري النقل إلى Supabase...")
    
    try:
        # نقل على دفعات (batch) لتجنب مشاكل الذاكرة
        batch_size = 50
        total_migrated = 0
        
        for i in range(0, chunk_count, batch_size):
            end = min(i + batch_size, chunk_count)
            
            batch_ids = ids[i:end]
            batch_embeddings = embeddings[i:end]
            batch_documents = documents[i:end]
            batch_metadatas = metadatas[i:end]
            
            # إضافة إلى Supabase
            add_documents_to_supabase(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas,
                embeddings=batch_embeddings
            )
            
            total_migrated += len(batch_ids)
            percentage = (total_migrated / chunk_count) * 100
            print(f"   ✅ {total_migrated}/{chunk_count} ({percentage:.1f}%)")
        
        print(f"\n🎉 اكتملت الهجرة بنجاح!")
        print(f"   - تم نقل: {total_migrated} chunks")
        
        # التحقق من النتيجة
        print("\n🔍 التحقق من النتيجة...")
        supabase = get_supabase()
        result = supabase.rpc('check_migration_status').execute()
        
        if result.data and len(result.data) > 0:
            stats = result.data[0]
            print(f"   - إجمالي الصفوف: {stats['total_rows']}")
            print(f"   - الصفوف مع embeddings: {stats['rows_with_embeddings']}")
            print(f"   - النسبة: {stats['percentage']}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ أثناء النقل: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # البحث عن أحدث backup file
    import glob
    import os
    
    backup_files = glob.glob("backups/chromadb_backup_*.pkl")
    
    if not backup_files:
        print("❌ لم يتم العثور على ملفات backup")
        sys.exit(1)
    
    # اختيار أحدث ملف
    latest_backup = max(backup_files, key=os.path.getctime)
    print(f"📁 استخدام الملف: {latest_backup}")
    
    # السؤال: وضع اختبار أم إنتاج؟
    print("\n" + "="*60)
    print("⚠️  هل تريد:")
    print("   1. وضع الاختبار (5 chunks فقط)")
    print("   2. النقل الكامل (جميع الـ chunks)")
    print("="*60)
    
    choice = input("اختر (1 أو 2): ").strip()
    
    test_mode = (choice != "2")
    
    # تنفيذ الهجرة
    success = migrate_chromadb_to_supabase(latest_backup, test_mode=test_mode)
    
    if success:
        print("\n✅ العملية اكتملت بنجاح!")
    else:
        print("\n❌ فشلت العملية")
        sys.exit(1)
