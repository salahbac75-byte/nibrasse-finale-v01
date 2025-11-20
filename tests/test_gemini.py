import google.generativeai as genai
from app.core.config import settings
import os

print("Configuring Gemini...")
genai.configure(api_key=settings.GEMINI_API_KEY)

def test_gemini():
    print("Testing Embedding...")
    try:
        result = genai.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            content="مرحبا بك",
            task_type="retrieval_document"
        )
        print("Embedding Success!")
        print(f"Vector length: {len(result['embedding'])}")
    except Exception as e:
        print(f"Embedding Failed: {e}")

if __name__ == "__main__":
    test_gemini()
