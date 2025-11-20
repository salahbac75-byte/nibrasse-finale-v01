"""
Quick test script for re-ranking functionality
"""
from app.services.rag import rag_pipeline

# Test the problematic short query
query = "ما دور الإعلام في تشكيل الوعي؟"

print(f"Testing query: {query}")
print("=" * 60)

try:
    result = rag_pipeline(query)
    print(f"\n✅ Query processed successfully!")
    print(f"\nAnswer preview: {result['answer'][:200]}...")
    print(f"\nContext sources: {len(result['context'])} chunks")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
