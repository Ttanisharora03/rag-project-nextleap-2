import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    print("Testing GET /api/health...")
    response = client.get("/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_schemes():
    print("Testing GET /api/schemes...")
    response = client.get("/api/schemes")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_chat():
    print("Testing POST /api/chat...")
    payload = {"query": "What is the expense ratio for ICICI Prudential Large Cap Fund?"}
    response = client.post("/api/chat", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    print("--- API Tests ---")
    test_health()
    test_schemes()
    test_chat()
    print("--- Tests Complete ---")
