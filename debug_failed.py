"""
Debug failed test cases
"""
from app.services.rag import rag_pipeline

# Test the two failed questions
failed_questions = [
    "ما هي أهم إنجازات الطب في الحضارة الإسلامية؟",
    "ما دور الخيال العلمي في استكشاف الفضاء؟"
]

for q in failed_questions:
    print(f"\n{'='*80}")
    print(f"Question: {q}")
    print('='*80)
    
    result = rag_pipeline(q)
    
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nContext sources: {len(result['context'])}")
    
    if result['context']:
        print("\nFirst chunk preview:")
        print(result['context'][0][:300] + "...")
