"""
Document chunker for mutual fund data.
Generates a 'Golden Chunk' from key-value pairs and uses LangChain to split the rest.
"""
import json
import logging
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_golden_chunk(data: dict[str, Any]) -> Document | None:
    """
    Creates a highly structured natural language chunk containing the most
    critical facts about the mutual fund scheme.
    """
    kv = data.get("extracted_kv", {})
    if not kv:
        return None
        
    scheme_name = data.get("scheme_name", "Unknown Scheme")
    category = data.get("category", "Unknown Category")
    
    sentences = [f"Scheme: {scheme_name} (Category: {category})."]
    
    for key, value in kv.items():
        # Clean up the key/value phrasing slightly to sound natural
        sentences.append(f"The {key} is {value}.")
        
    content = " ".join(sentences)
    
    metadata = {
        "source_url": data.get("source_url", ""),
        "scheme_name": scheme_name,
        "chunk_type": "golden_facts"
    }
    
    return Document(page_content=content, metadata=metadata)


def chunk_document(file_path: Path) -> list[Document]:
    """Reads a processed JSON file and splits it into LangChain Documents."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    scheme_name = data.get("scheme_name", "Unknown Scheme")
    source_url = data.get("source_url", "")
    content = data.get("content", "")
    
    documents = []
    
    # 1. Generate and append the Golden Chunk
    golden_doc = generate_golden_chunk(data)
    if golden_doc:
        documents.append(golden_doc)
        
    # 2. Split the remaining content using RecursiveCharacterTextSplitter
    # 500 characters isn't 500 tokens, but for LangChain default it splits by characters.
    # To approximate ~500 tokens, we use ~2000 characters.
    # The original plan said "~500 tokens", we'll use chunk_size=2000 chars and overlap=200 chars.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    # Create a base metadata dictionary for these chunks
    base_metadata = {
        "source_url": source_url,
        "scheme_name": scheme_name,
        "chunk_type": "detailed_text"
    }
    
    # Split text
    split_texts = text_splitter.split_text(content)
    
    # Create Document objects
    for text in split_texts:
        documents.append(Document(page_content=text, metadata=base_metadata))
        
    return documents


def run_chunker() -> list[Document]:
    """Chunk all processed files and return the full list of Documents."""
    processed_files = list(PROCESSED_DATA_DIR.glob("*_processed.json"))
    if not processed_files:
        logger.warning("No processed files found in data/processed/")
        return []
        
    all_documents = []
    
    for f in processed_files:
        docs = chunk_document(f)
        all_documents.extend(docs)
        logger.info(f"Chunked {f.name} into {len(docs)} documents.")
        
    logger.info(f"Chunking complete. Total documents: {len(all_documents)}")
    return all_documents


if __name__ == "__main__":
    docs = run_chunker()
    if docs:
        print(f"\nSample Golden Chunk:\n{docs[0].page_content}")
