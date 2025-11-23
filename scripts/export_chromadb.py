"""
Script لتصدير بيانات ChromaDB كنسخة احتياطية
"""
import chromadb
import pickle
import os
from datetime import datetime

def export_chromadb():
    """تصدير جميع بيانات ChromaDB إلى ملف pickle"""
    
    print("🔄 جاري تصدير بيانات ChromaDB...")
    
    # الاتصال بـ ChromaDB المحلي
    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_collection("rag_collection")
        
        # استخراج جميع البيانات
        all_data = collection.get(include=['embeddings', 'documents', 'metadatas'])
        
        # إنشاء مجلد backups
        os.makedirs('backups', exist_ok=True)
        
        # اسم الملف بالتاريخ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'backups/chromadb_backup_{timestamp}.pkl'
        
        # حفظ في ملف pickle (يدعم numpy arrays مباشرة)
        backup_data = {
            'export_date': timestamp,
            'total_chunks': len(all_data['ids']),
            'collection_name': 'rag_collection',
            'data': {
                'ids': all_data['ids'],
                'embeddings': all_data['embeddings'],
                'documents': all_data['documents'],
                'metadatas': all_data['metadatas']
            }
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(backup_data, f)
        
        print(f"✅ تم تصدير {len(all_data['ids'])} chunks بنجاح")
        print(f"📁 الملف: {filename}")
        print(f"💾 الحجم: {os.path.getsize(filename) / 1024 / 1024:.2f} MB")
        
        # إحصائيات إضافية
        print("\n📊 إحصائيات:")
        unique_docs = len(set(m.get('document_id', '') for m in all_data['metadatas']))
        print(f"   - عدد المستندات الفريدة: {unique_docs}")
        print(f"   - عدد الـ chunks: {len(all_data['ids'])}")
        
        return filename
        
    except Exception as e:
        print(f"❌ خطأ في التصدير: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    export_chromadb()
