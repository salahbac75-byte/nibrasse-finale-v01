"""
Comprehensive test suite for RAG system accuracy
"""
from app.services.rag import rag_pipeline
import time

# Test questions covering all documents
test_questions = [
    {
        "question": "ما هي أهم إنجازات الطب في الحضارة الإسلامية؟",
        "expected_doc": "الطب في الحضارة الإسلامية",
        "category": "تاريخ"
    },
    {
        "question": "كيف أثرت الثورة الرقمية على المجتمع العربي؟",
        "expected_doc": "الثورة الرقمية والمجتمع العربي",
        "category": "تكنولوجيا"
    },
    {
        "question": "ما العلاقة بين البيئة والتنمية المستدامة؟",
        "expected_doc": "البيئة والتنمية المستدامة",
        "category": "بيئة"
    },
    {
        "question": "اذكر خصائص الأدب العربي القديم",
        "expected_doc": "الأدب العربي القديم وجمال البيان",
        "category": "أدب"
    },
    {
        "question": "ما دور الخيال العلمي في استكشاف الفضاء؟",
        "expected_doc": "استكشاف الفضاء والخيال العلمي",
        "category": "علوم"
    },
    # Short queries (challenging)
    {
        "question": "ما هو الإعلام؟",
        "expected_doc": "الإعلام والوعي المجتمعي",
        "category": "قصير"
    },
    {
        "question": "اللغة والهوية",
        "expected_doc": "اللغة العربية والهوية الثقافية",
        "category": "قصير جداً"
    },
]

def extract_source_from_answer(answer: str) -> str:
    """Extract the main source document from answer"""
    if "**المراجع:**" in answer:
        refs_section = answer.split("**المراجع:**")[1]
        lines = refs_section.strip().split('\n')
        if lines:
            # Get first reference
            first_ref = lines[0].strip()
            # Remove [1], [2], etc.
            import re
            clean_ref = re.sub(r'^\[\d+\]\s*', '', first_ref)
            return clean_ref.strip()
    return ""

def run_tests():
    print("=" * 80)
    print("🧪 RAG System Comprehensive Test Suite")
    print("=" * 80)
    
    results = []
    total_time = 0
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n[{i}/{len(test_questions)}] Testing: {test['question']}")
        print(f"Category: {test['category']}")
        print(f"Expected: {test['expected_doc']}")
        
        start_time = time.time()
        try:
            result = rag_pipeline(test['question'])
            elapsed = time.time() - start_time
            total_time += elapsed
            
            # Extract source
            source = extract_source_from_answer(result['answer'])
            
            # Check if correct
            is_correct = test['expected_doc'].lower() in source.lower()
            
            results.append({
                "question": test['question'],
                "expected": test['expected_doc'],
                "actual": source,
                "correct": is_correct,
                "time": elapsed,
                "category": test['category']
            })
            
            status = "✅ PASS" if is_correct else "❌ FAIL"
            print(f"Result: {source}")
            print(f"Status: {status} ({elapsed:.2f}s)")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "question": test['question'],
                "expected": test['expected_doc'],
                "actual": f"ERROR: {str(e)}",
                "correct": False,
                "time": 0,
                "category": test['category']
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['correct'])
    total = len(results)
    accuracy = (passed / total * 100) if total > 0 else 0
    avg_time = total_time / total if total > 0 else 0
    
    print(f"\n✅ Passed: {passed}/{total} ({accuracy:.1f}%)")
    print(f"⏱️  Average time: {avg_time:.2f}s")
    print(f"⏱️  Total time: {total_time:.2f}s")
    
    # Category breakdown
    print("\n📂 By Category:")
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {'passed': 0, 'total': 0}
        categories[cat]['total'] += 1
        if r['correct']:
            categories[cat]['passed'] += 1
    
    for cat, stats in categories.items():
        cat_accuracy = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({cat_accuracy:.1f}%)")
    
    # Failed tests
    failed = [r for r in results if not r['correct']]
    if failed:
        print("\n❌ Failed Tests:")
        for r in failed:
            print(f"  - {r['question']}")
            print(f"    Expected: {r['expected']}")
            print(f"    Got: {r['actual']}")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    results = run_tests()
