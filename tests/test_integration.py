from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_upload_and_query():
    # 1. Test Upload
    file_path = "data/test_doc.txt"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print("Testing Upload...")
    with open(file_path, "rb") as f:
        response = client.post("/api/upload", files={"file": ("test_doc.txt", f, "text/plain")})
    
    if response.status_code != 200:
        print(f"Upload Failed: {response.text}")
        return
    
    print("Upload Success!")
    print(response.json())
    
    # 2. Test Query
    print("\nTesting Query...")
    query_payload = {"query": "ما هو الذكاء الاصطناعي؟"}
    response = client.post("/api/query", json=query_payload)
    
    if response.status_code != 200:
        print(f"Query Failed: {response.text}")
        return

    print("Query Success!")
    print(response.json())

if __name__ == "__main__":
    test_upload_and_query()
