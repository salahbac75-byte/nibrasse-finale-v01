"""
اختبار البحث الفيكتوري في Supabase v2
"""
import sys
import os
import json

# إضافة project root إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.vector_store_supabase import query_supabase_vectors
from app.services.embedding import get_embedding

def test_search_v2():
    """
    اختبار البحث عن جملة موجودة في المستند المرفوع
    """
    print("="*70)
    print("🔍 اختبار البحث الفيكتوري (v2)")
    print("="*70)
    
    # جملة من المستند الذي رفعناه
    query_text = "L'intelligence artificielle transforme notre monde"
    
    print(f"\n📝 السؤال: {query_text}")
    print("\n🔄 جاري توليد embedding للسؤال...")
    
    try:
        query_embedding = get_embedding(query_text, is_query=True)
        print(f"✅ تم توليد embedding ({len(query_embedding)} dimensions)")
        
        # البحث
        print("\n🔍 جاري البحث في Supabase v2...")
        results = query_supabase_vectors(query_embedding, n_results=3)
        
        # عرض النتائج
        print("\n" + "="*70)
        print("📊 نتائج البحث:")
        print("="*70)
        
        if not results['documents'][0]:
            print("❌ لم يتم العثور على أي نتائج!")
            return False
            
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"\n【 النتيجة {i} 】")
            print(f"   📄 المحتوى: {doc[:150]}...")
            print(f"   📊 Distance: {dist:.4f}")
            print(f"   📁 الملف: {meta.get('filename', 'N/A')}")
            
            # تقييم النتيجة
            if dist < 0.5:
                print("   ✅ تطابق قوي جداً")
            elif dist < 0.7:
                print("   ✅ تطابق جيد")
            else:
                print("   ⚠️ تطابق ضعيف")
                
        print("\n" + "="*70)
        print("🎉 البحث يعمل بنجاح!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ أثناء البحث: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_search_v2()
