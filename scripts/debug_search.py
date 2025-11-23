"""
اختبار البحث المباشر (بدون RPC)
"""
import sys
import os

# إضافة project root إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.database import get_supabase
from app.services.embedding import get_embedding

def test_direct_search():
    print("="*70)
    print("🔍 اختبار البحث المباشر (Direct SQL)")
    print("="*70)
    
    query_text = "L'intelligence artificielle transforme notre monde"
    query_embedding = get_embedding(query_text, is_query=True)
    
    # تحويل embedding لنص SQL format
    emb_str = str(query_embedding)
    
    supabase = get_supabase()
    
    # محاولة استعلام مباشر (إذا كان مسموحاً)
    # ملاحظة: Supabase client لا يدعم raw SQL select بسهولة، 
    # لكن يمكننا استخدام RPC بسيط جداً للdebug
    
    print("\n🔄 محاولة استدعاء RPC مع debug...")
    
    try:
        # نستخدم نفس RPC لكن نتأكد من الـ params
        params = {
            'query_embedding': query_embedding, # list
            'match_count': 5
        }
        
        result = supabase.rpc('match_chunks_v2', params).execute()
        
        print(f"\n📊 Raw Result Data: {result.data}")
        
        if not result.data:
            print("\n❌ النتيجة فارغة تماماً!")
            
            # التحقق من وجود أي بيانات أصلاً
            count = supabase.table('chunks_v2').select('count', count='exact').execute()
            print(f"   - عدد الصفوف في الجدول: {count.count}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_direct_search()
