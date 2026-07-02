"""
Document indexer for mutual fund data.
Embeds chunks and stores them in ChromaDB.
"""
import logging
from pathlib import Path
import shutil

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from src.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL
from src.ingestion.chunker import run_chunker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def init_embeddings() -> HuggingFaceBgeEmbeddings:
    """Initialize the BGE-small embedding model."""
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    
    # We use CPU by default for stability unless a GPU is available.
    # BGE-small is very fast on CPU.
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True} # BGE models require normalized embeddings
    
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embeddings


def run_indexer():
    """Run the indexing pipeline: Chunk -> Embed -> Store in ChromaDB."""
    # 1. Get documents from chunker
    logger.info("Starting chunking process...")
    documents = run_chunker()
    
    if not documents:
        logger.error("No documents returned from chunker. Aborting indexing.")
        return
        
    # 2. Clear old vectorstore if it exists (for idempotency)
    persist_path = Path(CHROMA_PERSIST_DIR)
    if persist_path.exists():
        logger.info(f"Clearing existing vectorstore at {persist_path}")
        shutil.rmtree(persist_path)
        
    persist_path.mkdir(parents=True, exist_ok=True)
    
    # 3. Initialize embeddings
    embeddings = init_embeddings()
    
    # 4. Store in ChromaDB
    logger.info(f"Indexing {len(documents)} chunks into ChromaDB at {persist_path}...")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION,
        persist_directory=str(persist_path)
    )
    
    logger.info("Indexing complete and persisted to vectorstore.")
    return vectorstore


if __name__ == "__main__":
    run_indexer()
