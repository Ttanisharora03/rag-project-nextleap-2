import sys
import os
import logging
from pathlib import Path

# Add project root to path so we can import src modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.query import query_rag

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    queries = [
        "What is the expense ratio of ICICI Prudential Large Cap Fund?",
        "Should I invest my money in the Large Cap Fund?",
        "My PAN number is ABCDE1234F, can you check my portfolio?",
        "What is the weather today?"
    ]
    
    for q in queries:
        print(f"\n{'='*50}\nQuery: {q}\n{'-'*50}")
        try:
            response = query_rag(q)
            print(f"Classification: {response['classification']}")
            print(f"Type: {response['type']}")
            print(f"Answer:\n{response['answer']}")
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()
