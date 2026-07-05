import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# Add project root to path so we can import from src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma
from src.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION

def view_embeddings(limit=3):
    print(f"Loading ChromaDB from {CHROMA_PERSIST_DIR} (Collection: {CHROMA_COLLECTION})")
    
    # Initialize Chroma db connected to our persistence directory
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=CHROMA_COLLECTION
    )
    
    # Fetch data including embeddings
    # .get() by default fetches documents and metadatas, but we must explicitly include embeddings
    result = db.get(include=["documents", "metadatas", "embeddings"], limit=limit)
    
    ids = result["ids"]
    documents = result["documents"]
    metadatas = result["metadatas"]
    embeddings = result["embeddings"]
    
    print(f"\nFound {len(ids)} chunks in the vectorstore. Showing first {limit}:\n")
    
    for i in range(len(ids)):
        print("-" * 60)
        print(f"Chunk ID: {ids[i]}")
        print(f"Metadata: {metadatas[i]}")
        
        # Truncate document text for display
        doc_text = documents[i].replace('\n', ' ')
        display_text = doc_text if len(doc_text) <= 150 else doc_text[:150] + "..."
        print(f"Text Preview: {display_text}")
        
        # Display embedding information
        if embeddings is not None and len(embeddings) > i and embeddings[i] is not None:
            emb = embeddings[i]
            # Show first 5 dimensions as a preview
            preview_vector = [round(val, 4) for val in emb[:5]]
            print(f"Embedding Dimensions: {len(emb)}")
            print(f"Embedding Preview (first 5 dims): {preview_vector}")
        else:
            print("Embedding: None or not found")
            
    print("-" * 60)

if __name__ == "__main__":
    view_embeddings(limit=3)
