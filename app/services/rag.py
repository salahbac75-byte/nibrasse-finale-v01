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

def detect_language(text: str) -> str:
    """Detect the language of the query"""
    # Simple heuristic based on character sets
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    total_chars = len([c for c in text if c.isalpha()])
    
    if total_chars == 0:
        return "ar"  # Default to Arabic
    
    arabic_ratio = arabic_chars / total_chars
    
    if arabic_ratio > 0.3:
        return "ar"  # Arabic
    
    # Check for French specific words
    french_words = ['le', 'la', 'les', 'de', 'et', 'dans', 'pour', 'sont', 'peut', 'comment', 'quels', 'quel']
    text_lower = text.lower()
    if any(word in text_lower.split() for word in french_words):
        return "fr"  # French
    
    return "en"  # Default to English

def generate_answer(query: str, context: str, metadatas: list = None) -> str:
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    # Detect query language
    lang = detect_language(query)
    
    # Language-specific instructions
    lang_instructions = {
        "ar": "أجب بالعربية الفصحى",
        "fr": "Répondez en français",
        "en": "Answer in English"
    }
    
    lang_prompt = lang_instructions.get(lang, lang_instructions["ar"])
    
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

**IMPORTANT: {lang_prompt}**

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
   - التنسيق: **المراجع:** (أو **Références:** للفرنسية أو **References:** للإنجليزية)
     [1] عنوان المصدر الأول
     [2] عنوان المصدر الثاني (إن وُجد)

**قواعد صارمة:**
- لا تخترع معلومات غير موجودة في المصادر
- لا تستشهد بمصادر لم تستخدمها
- إذا كان مصدر واحد كافياً، لا تستخدم مصادر إضافية
- **أجب بنفس لغة السؤال: {lang_prompt}**

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

def rerank_with_gemini(query: str, chunks: list[str], top_k: int = 3) -> list[tuple[str, float]]:
    """
    Use Gemini to re-rank chunks based on relevance to query.
    Returns list of (chunk, score) tuples sorted by relevance.
    """
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    # Prepare chunks for evaluation
    chunks_text = ""
    for i, chunk in enumerate(chunks[:10], 1):  # Evaluate top 10 only
        chunks_text += f"\n\n### Chunk {i}:\n{chunk[:500]}...\n"  # Limit chunk size
    
    prompt = f"""قيّم مدى صلة كل chunk بالسؤال التالي. أعط درجة من 0 إلى 10 لكل chunk.

**السؤال:**
{query}

**Chunks:**
{chunks_text}

**التعليمات:**
- أعط درجة 10 إذا كان الـ chunk يجيب مباشرة على السؤال
- أعط درجة 5-9 إذا كان الـ chunk ذو صلة جزئية
- أعط درجة 0-4 إذا كان الـ chunk غير ذي صلة

**الإجابة المطلوبة (JSON فقط):**
```json
{{
  "1": 8,
  "2": 3,
  "3": 9,
  ...
}}
```
"""
    
    try:
        response = model.generate_content(prompt)
        # Extract JSON from response
        import json
        import re
        
        # Find JSON in response
        json_match = re.search(r'\{[^}]+\}', response.text)
        if json_match:
            scores = json.loads(json_match.group())
            
            # Create ranked list
            ranked = []
            for i, chunk in enumerate(chunks[:10], 1):
                score = float(scores.get(str(i), 0)) / 10.0  # Normalize to 0-1
                ranked.append((chunk, score))
            
            # Add remaining chunks with low score
            for chunk in chunks[10:]:
                ranked.append((chunk, 0.1))
            
            # Sort by score
            ranked.sort(key=lambda x: x[1], reverse=True)
            return ranked[:top_k]
        else:
            # Fallback: return top chunks as-is
            return [(chunk, 0.5) for chunk in chunks[:top_k]]
            
    except Exception as e:
        print(f"Re-ranking error: {e}")
        # Fallback: return top chunks as-is
        return [(chunk, 0.5) for chunk in chunks[:top_k]]

def rag_pipeline(query: str):
    from app.services.query_expansion import expand_query
    
    # 1. Expand query for better coverage (activate for queries with 10 words or less)
    queries = expand_query(query) if len(query.split()) <= 10 else [query]
    print(f"Searching with {len(queries)} query variations...")
    
    # 2. Search with all query variations and collect results
    all_documents = []
    all_distances = []
    all_metadatas = []
    
    for q in queries:
        # Embed Query with correct task_type
        query_embedding = get_embedding(q, is_query=True)
        
        # Retrieve from ChromaDB
        results = query_chroma(query_embedding, n_results=10)
        
        # Collect results
        all_documents.extend(results['documents'][0])
        all_distances.extend(results['distances'][0] if 'distances' in results else [0] * len(results['documents'][0]))
        all_metadatas.extend(results.get('metadatas', [[]])[0] if results.get('metadatas') else [{}] * len(results['documents'][0]))
    
    # 3. Deduplicate and score
    seen = set()
    unique_docs_with_scores = []
    unique_metadatas = []
    
    for doc, dist, meta in zip(all_documents, all_distances, all_metadatas):
        # Use first 100 chars as fingerprint
        fingerprint = doc[:100]
        if fingerprint not in seen:
            seen.add(fingerprint)
            
            # Calculate hybrid score using ORIGINAL query
            semantic_score = 1.0 / (1.0 + dist) if dist > 0 else 1.0
            keyword_score = calculate_relevance_score(query, doc)
            
            # Weighted combination (70% semantic, 30% keyword)
            hybrid_score = 0.7 * semantic_score + 0.3 * keyword_score
            
            unique_docs_with_scores.append((doc, hybrid_score))
            unique_metadatas.append(meta)
    
    # 4. Re-rank by hybrid score
    ranked_items = sorted(zip(unique_docs_with_scores, unique_metadatas), 
                         key=lambda x: x[0][1], reverse=True)
    
    # Take top 10 for re-ranking
    top_10_documents = [doc for (doc, score), meta in ranked_items[:10]]
    top_10_metadatas = [meta for (doc, score), meta in ranked_items[:10]]
    
    # 5. Re-rank with Gemini for better accuracy
    reranked = rerank_with_gemini(query, top_10_documents, top_k=5)
    
    # Extract documents and find their metadata
    final_documents = []
    final_metadatas = []
    for chunk, score in reranked:
        # Find index in top_10
        try:
            idx = top_10_documents.index(chunk)
            final_documents.append(chunk)
            final_metadatas.append(top_10_metadatas[idx])
        except ValueError:
            # Fallback if not found
            final_documents.append(chunk)
            final_metadatas.append({})
    
    context = "\n\n---\n\n".join(final_documents)
    
    # 6. Generate Answer with metadata
    answer = generate_answer(query, context, final_metadatas)
    
    return {
        "query": query,
        "context": final_documents,
        "answer": answer
    }

