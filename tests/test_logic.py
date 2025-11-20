from app.services.ingestion import process_document
from app.services.rag import rag_pipeline
import os
import sys

def test_logic():
    with open("tests/result.txt", "w", encoding="utf-8") as log_file:
        # 1. Test Ingestion
        file_path = "data/test_doc.txt"
        if not os.path.exists(file_path):
            log_file.write(f"Error: {file_path} not found.\n")
            return

        log_file.write("Testing Ingestion Logic...\n")
        try:
            result = process_document(file_path)
            log_file.write("Ingestion Success!\n")
            log_file.write(str(result) + "\n")
        except Exception as e:
            log_file.write(f"Ingestion Failed: {e}\n")
            return
        
        # 2. Test RAG
        log_file.write("\nTesting RAG Logic...\n")
        try:
            query = "ما هو الذكاء الاصطناعي؟"
            result = rag_pipeline(query)
            log_file.write("RAG Success!\n")
            log_file.write(str(result) + "\n")
        except Exception as e:
            log_file.write(f"RAG Failed: {e}\n")

if __name__ == "__main__":
    test_logic()
