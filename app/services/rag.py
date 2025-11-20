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

def generate_answer(query: str, context: str, metadatas: list = None) -> str:
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    # Number each context chunk for reference with metadata
    context_chunks = context.split("\n\n---\n\n")
    numbered_context = ""
    source_titles = []
    
    for i, chunk in enumerate(context_chunks, 1):
        # Extract title from metadata if available
        if metadatas and i <= len(metadatas):
            # Use filename and clean it up (remove extension and special chars)
            filename = metadatas[i-1].get('filename', f'مصدر {i}')
            # Remove .txt extension and clean up the title
            title = filename.replace('.txt', '').replace('-', ' ').replace('_', ' ')
            source_titles.append(title)
            numbered_context += f"\n\n### [مصدر {i}: {title}]\n{chunk}\n"
        else:
            source_titles.append(f'مصدر {i}')
            numbered_context += f"\n\n### [مصدر {i}]\n{chunk}\n"

    
    prompt = f"""أنت مساعد ذكي متخصص في تقديم إجابات دقيقة واحترافية بأسلوب أكاديمي.

**تعليمات الإجابة:**

1. **ركّز على الدقة**: استخدم فقط المصادر الأكثر صلة بالسؤال
2. **الاستشهاد الذكي**: 
   - استشهد بمصدر واحد فقط إذا كان كافياً للإجابة
   - استخدم مصادر متعددة فقط إذا كانت الإجابة تتطلب ذلك فعلاً
   - ضع رقم المصدر [1] مباشرة بعد المعلومة المستقاة منه

3. **هيكل الإجابة**:
   - مقدمة موجزة (سطر واحد)
   - إجابة مباشرة ومنظمة في فقرات واضحة
   - استشهادات دقيقة بعد كل معلومة
   - قائمة مراجع في النهاية

4. **قائمة المراجع**:
   - اذكر فقط المصادر التي استخدمتها فعلياً في الإجابة
   - استخدم العناوين الموجودة في رأس كل مصدر
   - التنسيق: **المراجع:**
     [1] عنوان المصدر الأول
     [2] عنوان المصدر الثاني (إن وُجد)

**قواعد صارمة:**
- لا تخترع معلومات غير موجودة في المصادر
- لا تستشهد بمصادر لم تستخدمها
- إذا كان مصدر واحد كافياً، لا تستخدم مصادر إضافية
- اكتب بلغة عربية فصيحة وواضحة

**المصادر المتاحة:**
{numbered_context}

**السؤال:**
{query}

**الإجابة:**
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
    # 1. Embed Query with correct task_type
    query_embedding = get_embedding(query, is_query=True)
    
    # 2. Retrieve from ChromaDB (increased to 15 for better coverage)
    results = query_chroma(query_embedding, n_results=15)
    
    # 3. Extract Context and deduplicate
    documents = results['documents'][0]
    distances = results['distances'][0] if 'distances' in results else [0] * len(documents)
    metadatas = results.get('metadatas', [[]])[0]
    
    # Remove duplicates while preserving order and distances
    seen = set()
    unique_docs_with_scores = []
    unique_metadatas = []
    
    for doc, dist, meta in zip(documents, distances, metadatas if metadatas else [{}] * len(documents)):
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
            unique_metadatas.append(meta)
    
    # Re-rank by hybrid score
    ranked_items = sorted(zip(unique_docs_with_scores, unique_metadatas), 
                         key=lambda x: x[0][1], reverse=True)
    
    # Take top 5 most relevant documents
    top_documents = [doc for (doc, score), meta in ranked_items[:5]]
    top_metadatas = [meta for (doc, score), meta in ranked_items[:5]]
    
    context = "\n\n---\n\n".join(top_documents)
    
    # 4. Generate Answer with metadata
    answer = generate_answer(query, context, top_metadatas)
    
    return {
        "query": query,
        "context": top_documents,
        "answer": answer
    }
