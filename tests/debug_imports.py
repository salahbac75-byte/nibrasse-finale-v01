import os

log_file = "tests/import_log.txt"

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

if os.path.exists(log_file):
    os.remove(log_file)

log("Starting imports...")

try:
    log("Importing os...")
    import os
    log("Importing sys...")
    import sys
    log("Importing shutil...")
    import shutil
    log("Importing fastapi...")
    import fastapi
    log("Importing google.generativeai...")
    import google.generativeai
    log("Importing chromadb...")
    import chromadb
    log("Importing supabase...")
    import supabase
    log("Importing langchain_text_splitters...")
    import langchain_text_splitters
    log("Importing app.services.ingestion...")
    from app.services import ingestion
    log("Importing app.services.rag...")
    from app.services import rag
    log("All imports successful!")
except Exception as e:
    log(f"Import failed: {e}")
