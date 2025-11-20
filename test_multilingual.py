"""
Test multilingual responses
"""
from app.services.rag import rag_pipeline

# Test questions in different languages
test_questions = [
    ("Quels sont les principaux risques liés aux biais dans les systèmes d'IA?", "fr"),
    ("What is the role of media in shaping awareness?", "en"),
    ("ما دور الإعلام في تشكيل الوعي؟", "ar"),
]

for question, expected_lang in test_questions:
    print(f"\n{'='*80}")
    print(f"Question ({expected_lang}): {question}")
    print('='*80)
    
    result = rag_pipeline(question)
    answer = result['answer']
    
    # Show first 300 chars
    print(f"\nAnswer preview:\n{answer[:300]}...")
    print(f"\nExpected language: {expected_lang}")
