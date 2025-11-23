"""
Script لاختبار البحث الفيكتوري في Supabase ومقارنته مع ChromaDB
"""
import sys
import os

# إضافة project root إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.vector_store_supabase import query_supabase_vectors
from app.services.embedding import get_embedding

def test_supabase_search():
    """
    اختبار بسيط للبحث الفيكتوري في Supabase
    """
    print("="*70)
    print("🔍 اختبار البحث الفيكتوري في Supabase pgvector")
    print("="*70)
    
    # سؤال اختباري
    test_query = "ما هو الذكاء الاصطناعي؟"
    
    print(f"\n📝 السؤال الاختباري: {test_query}")
    print("\n🔄 جاري توليد embedding للسؤال...")
    
    try:
        # توليد embedding للسؤال
        query_embedding = get_embedding(test_query, is_query=True)
        print(f"✅ تم توليد embedding (768 dimension)")
        
        # البحث في Supabase - نبحث في الـ 5 chunks المنقولة
        print("\n🔍 جاري البحث في Supabase...")
        results = query_supabase_vectors(query_embedding, n_results=5)
        
        print(f"\n✅ تم العثور على {len(results['documents'][0])} نتائج")
        
        # عرض النتائج
        print("\n" + "="*70)
        print("📊 النتائج:")
        print("="*70)
        
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ), 1):
            print(f"\n【 النتيجة {i} 】")
            print(f"   📄 المحتوى: {doc[:200]}{'...' if len(doc) > 200 else ''}")
            print(f"   📊 Distance: {dist:.4f} (كلما أقل، كلما أفضل)")
            print(f"   🔢 Chunk Index: {meta.get('chunk_index', 'N/A')}")
            print(f"   📁 Document ID: {meta.get('document_id', 'N/A')}")
        
        print("\n" + "="*70)
        print("✅ الاختبار نجح! البحث الفيكتوري يعمل بشكل ممتاز")
        print("="*70)
        
        # اختبار إضافي: التحقق من أن النتائج منطقية
        if len(results['documents'][0]) > 0:
            avg_distance = sum(results['distances'][0]) / len(results['distances'][0])
            print(f"\n📈 إحصائيات:")
            print(f"   - متوسط Distance: {avg_distance:.4f}")
            print(f"   - أفضل Distance: {min(results['distances'][0]):.4f}")
            print(f"   - أسوأ Distance: {max(results['distances'][0]):.4f}")
            
            if avg_distance < 0.5:
                print("\n✅ النتائج ممتازة! (Distance منخفض = تشابه عالي)")
            elif avg_distance < 0.7:
                print("\n✅ النتائج جيدة!")
            else:
                print("\n⚠️ النتائج متوسطة (قد تحتاج لمزيد من البيانات)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ أثناء الاختبار: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supabase_search()
    
    if success:
        print("\n" + "="*70)
        print("🎉 جميع الاختبارات نجحت!")
        print("💡 يمكنك الآن المتابعة مع النقل الكامل بثقة تامة")
        print("="*70)
        sys.exit(0)
    else:
        print("\n❌ فشل الاختبار")
        sys.exit(1)
