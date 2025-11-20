"""
Query expansion service to improve search for short queries
"""
import google.generativeai as genai
from app.core.config import settings
from app.services.embedding import configure_gemini

def expand_query(query: str) -> list[str]:
    """
    Expand a short query into multiple related queries for better search coverage.
    Returns list of query variations including the original.
    """
    configure_gemini()
    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
    
    prompt = f"""أنت خبير في توسيع الاستعلامات البحثية. 

**السؤال الأصلي:**
{query}

**المطلوب:**
اكتب 3-4 صيغ بديلة لهذا السؤال تساعد في البحث عن نفس المعلومة. يجب أن تكون الصيغ:
- أكثر تفصيلاً من السؤال الأصلي
- تحتوي على كلمات مفتاحية مختلفة
- تغطي جوانب مختلفة من السؤال

**مثال:**
السؤال: "ما دور الإعلام في تشكيل الوعي؟"
الصيغ البديلة:
1. كيف يؤثر الإعلام على الوعي المجتمعي والثقافي؟
2. ما هي آليات تشكيل الوعي من خلال وسائل الإعلام؟
3. كيف تساهم وسائل الإعلام في بناء الوعي والتربية الإعلامية؟

**الآن، اكتب الصيغ البديلة للسؤال المعطى (كل صيغة في سطر منفصل):**
"""
    
    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n')
        
        # Extract queries (remove numbering and empty lines)
        expanded = [query]  # Always include original
        for line in lines:
            line = line.strip()
            # Remove numbering like "1.", "2.", etc.
            import re
            clean_line = re.sub(r'^\d+[\.\)]\s*', '', line)
            if clean_line and len(clean_line) > 10:
                expanded.append(clean_line)
        
        return expanded[:4]  # Return max 4 queries (original + 3 expansions)
        
    except Exception as e:
        print(f"Query expansion error: {e}")
        return [query]  # Fallback to original query only
