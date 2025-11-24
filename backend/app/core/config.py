import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
    SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
    GEMINI_CHAT_MODEL = os.getenv("VITE_GEMINI_CHAT_MODEL")
    GEMINI_EMBEDDING_MODEL = os.getenv("VITE_GEMINI_EMBEDDING_MODEL")

settings = Settings()
