"""
Script لفحص بنية embeddings في backup file
"""
import pickle
import numpy as np

def inspect_backup_embeddings():
    """
    فحص بنية embeddings في backup file
    """
    print("="*70)
    print("🔍 فحص بنية Embeddings في Backup")
    print("="*70)
    
    # قراءة backup
    backup_file = "backups/chromadb_backup_20251123_132453.pkl"
    
    print(f"\n📁 قراءة: {backup_file}")
    
    with open(backup_file, 'rb') as f:
        backup_data = pickle.load(f)
    
    embeddings = backup_data['data']['embeddings']
    
    print(f"\n📊 معلومات عامة:")
    print(f"   - عدد الـ embeddings: {len(embeddings)}")
    print(f"   - نوع البيانات: {type(embeddings)}")
    
    # فحص أول embedding
    first_emb = embeddings[0]
    
    print(f"\n🔬 فحص أول embedding:")
    print(f"   - النوع: {type(first_emb)}")
    print(f"   - الشكل (shape): {first_emb.shape if hasattr(first_emb, 'shape') else 'N/A'}")
    
    if hasattr(first_emb, 'shape'):
        print(f"   - عدد الأبعاد (ndim): {first_emb.ndim}")
    
    # التحويل لـ list والتحقق
    print(f"\n🔄 اختبار التحويل:")
   
    emb_list = first_emb.tolist()
    print(f"   - نوع بعد .tolist(): {type(emb_list)}")
    print(f"   - الطول: {len(emb_list)}")
    
    # التحقق من البنية
    if isinstance(emb_list, list):
        if len(emb_list) > 0:
            print(f"   - نوع العنصر الأول: {type(emb_list[0])}")
            if isinstance(emb_list[0], (list, np.ndarray)):
                print(f"   ⚠️ تحذير: Embedding هو nested list!")
                print(f"   - طول العنصر الأول: {len(emb_list[0])}")
                # محاولة flatten
                flat = np.array(emb_list).flatten().tolist()
                print(f"   - بعد flatten: {len(flat)} dimensions")
            else:
                print(f"   ✅ Embedding صحيح - flat list")
    
    # عرض عينة صغيرة
    print(f"\n📝 عينة من أول 10 قيم:")
    sample = emb_list[:10] if isinstance(emb_list, list) else []
    for i, val in enumerate(sample):
        print(f"   [{i}]: {val} (type: {type(val).__name__})")
    
    print("\n" + "="*70)
    
    return embeddings

if __name__ == "__main__":
    inspect_backup_embeddings()
