import google.generativeai as genai
from app.core.config import settings
from app.services.embedding import get_embedding
from app.services.vector_store import query_chroma

_gemini_configured = False

def configure_gemini():
    global _gemini_configured
    if not _gemini_configured:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_configured = True

def generate_answer(query: str, context: str) -> str:
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    # Number each context chunk for reference
    context_chunks = context.split("\n\n---\n\n")
    numbered_context = ""
    for i, chunk in enumerate(context_chunks, 1):
        numbered_context += f"\n\n### [مصدر {i}]\n{chunk}\n"
    
    prompt = f"""أنت مساعد ذكي متخصص في تقديم إجابات احترافية ومنظمة بأسلوب أكاديمي.

عند الإجابة على الأسئلة، اتبع هذا الهيكل بدقة:

1. **المقدمة**: ابدأ بتمهيد قصير (2-3 أسطر) يضع السؤال في سياقه
2. **الإجابة الرئيسية**: قدم إجابة شاملة ومنظمة في فقرات واضحة
3. **الاستشهادات**: استخدم أرقام بين قوسين [1]، [2]، [3] للإشارة إلى المصادر
4. **المراجع**: في النهاية، أدرج قائمة المراجع المرقمة بالتنسيق التالي:

**المراجع:**
[1] [عنوان واضح من المصدر الأول]
[2] [عنوان واضح من المصدر الثاني]
...إلخ

**قواعد مهمة:**
- استخدم لغة عربية فصيحة واضحة
- نظّم الإجابة في فقرات متماسكة (كل فقرة 3-4 أسطر)
- استشهد بالمصادر في نهاية كل جملة أو فكرة رئيسية
- في قسم المراجع، استخرج العنوان الفعلي من كل مصدر (ابحث عن "العنوان:" في النص)
- إذا لم تجد عنواناً واضحاً، اكتب ملخصاً قصيراً للمصدر (10-15 كلمة)
- لا تخترع معلومات غير موجودة في السياق
- إذا لم تجد الإجابة في السياق، قل ذلك بوضوح

**المصادر المتاحة:**
{numbered_context}

**السؤال:**
{query}

**الإجابة المطلوبة:**
قدم إجابة احترافية منظمة مع استشهادات مرقمة ومراجع واضحة في الأسفل.
"""
    response = model.generate_content(prompt)
    return response.text

def calculate_relevance_score(query: str, document: str) -> float:
    """Calculate relevance score using keyword overlap"""
    query_words = set(query.lower().split())
    doc_words = set(document.lower().split())
    
    if len(query_words) == 0:
        return 0.0
    
    # Jaccard similarity
    intersection = query_words.intersection(doc_words)
    union = query_words.union(doc_words)
    
    return len(intersection) / len(union) if len(union) > 0 else 0.0

def rag_pipeline(query: str):
    # 1. Embed Query
    query_embedding = get_embedding(query)
    
    # 2. Retrieve from ChromaDB (increased to 15 for better coverage)
    results = query_chroma(query_embedding, n_results=15)
    
    # 3. Extract Context and deduplicate
    documents = results['documents'][0]
    distances = results['distances'][0] if 'distances' in results else [0] * len(documents)
    
    # Remove duplicates while preserving order and distances
    seen = set()
    unique_docs_with_scores = []
    
    for doc, dist in zip(documents, distances):
        # Use first 100 chars as fingerprint
        fingerprint = doc[:100]
        if fingerprint not in seen:
            seen.add(fingerprint)
            
            # Calculate hybrid score
            # Lower distance = more similar (convert to similarity: 1 - normalized_distance)
            semantic_score = 1.0 / (1.0 + dist) if dist > 0 else 1.0
            keyword_score = calculate_relevance_score(query, doc)
            
            # Weighted combination (70% semantic, 30% keyword)
            hybrid_score = 0.7 * semantic_score + 0.3 * keyword_score
            
            unique_docs_with_scores.append((doc, hybrid_score))
    
    # Re-rank by hybrid score
    unique_docs_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Take top 5 most relevant documents
    top_documents = [doc for doc, score in unique_docs_with_scores[:5]]
    
    context = "\n\n---\n\n".join(top_documents)
    
    # 4. Generate Answer
    answer = generate_answer(query, context)
    
    return {
        "query": query,
        "context": top_documents,
        "answer": answer
    }
