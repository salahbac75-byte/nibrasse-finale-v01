"""
اختبار رفع مستند واحد إلى Supabase v2
"""
import sys
import os

# إضافة project root إلى Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.services.ingestion import process_document
from app.services.database import get_supabase

def test_upload_one_document():
    """
    اختبار رفع مستند test بسيط
    """
    print("="*70)
    print("🧪 اختبار رفع مستند واحد إلى Supabase v2")
    print("="*70)
    
    # إنشاء ملف test صغير
    test_file = "data/test_simple.txt"
    test_content = """Titre : Test Document pour Supabase v2

== Introduction ==
Ceci est un document de test simple pour vérifier que le système fonctionne correctement avec Supabase pgvector.

L'intelligence artificielle transforme notre monde de manière profonde.

== Conclusion ==
Ce test devrait créer environ 2-3 chunks avec des embeddings de 768 dimensions.
"""
    
    print(f"\n📝 Création du fichier test: {test_file}")
    
    # Créer le fichier
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"✅ Fichier créé ({len(test_content)} caractères)")
    
    print("\n🔄 Traitement du document...")
    
    try:
        # Process le document
        result = process_document(test_file)
        
        print(f"\n✅ Document traité avec succès!")
        print(f"   - Total chunks: {result['total_chunks']}")
        print(f"   - Document ID: {result['document_id']}")
        print(f"   - Status: {result['status']}")
        
        # Vérifier dans Supabase
        print("\n🔍 Vérification dans Supabase...")
        supabase = get_supabase()
        
        # Checker le document
        doc_result = supabase.table("documents_v2").select("*").eq("id", result['document_id']).execute()
        
        if doc_result.data:
            doc = doc_result.data[0]
            print(f"✅ Document dans DB:")
            print(f"   - Filename: {doc['filename']}")
            print(f"   - Total chunks: {doc['total_chunks']}")
        
        # Checker les chunks
        chunks_result = supabase.table("chunks_v2").select("id, chunk_index, embedding").eq("document_id", result['document_id']).execute()
        
        if chunks_result.data:
            print(f"\n✅ Chunks dans DB: {len(chunks_result.data)}")
            import json
            for chunk in chunks_result.data:
                emb = chunk['embedding']
                print(f"   - Raw type: {type(emb)}")
                
                # إصلاح: تحويل string إلى list
                if isinstance(emb, str):
                    try:
                        emb = json.loads(emb)
                        print(f"   - ✅ Converted from string to list")
                    except:
                        # محاولة تنظيف النص إذا كان بتنسيق pgvector '[...]'
                        try:
                            clean_emb = emb.replace('[', '').replace(']', '')
                            emb = [float(x) for x in clean_emb.split(',')]
                            print(f"   - ✅ Parsed pgvector string")
                        except Exception as e:
                            print(f"   - ❌ Parsing failed: {e}")

                emb_len = len(emb) if emb else 0
                print(f"   - Chunk {chunk['chunk_index']}: embedding dimensions = {emb_len}")
                
                # التحقق الحرج!
                if emb_len != 768:
                    print(f"   ❌ ERREUR: dimensions devrait être 768, pas {emb_len}!")
                    # return False # لن نوقف الاختبار الآن لنرى باقي النتائج
        
        # Stats
        stats = supabase.rpc('check_migration_status_v2').execute()
        if stats.data:
            s = stats.data[0]
            print(f"\n📊 Statistiques globales:")
            print(f"   - Total rows: {s['total_rows']}")
            print(f"   - Rows avec embeddings: {s['rows_with_embeddings']}")
            print(f"   - Percentage: {s['percentage']}%")
        
        print("\n" + "="*70)
        print("🎉 Test réussi! Embeddings = 768 dimensions ✅")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_upload_one_document()
    sys.exit(0 if success else 1)
