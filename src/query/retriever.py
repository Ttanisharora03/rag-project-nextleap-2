"""
Retriever module.
Embeds the query and fetches relevant chunks from ChromaDB.
"""
import logging
from typing import List

# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma
# pyrefly: ignore [missing-import]
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
# pyrefly: ignore [missing-import]
from langchain_core.documents import Document

from src.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, RETRIEVER_TOP_K

logger = logging.getLogger(__name__)

# Global instances to avoid reloading on every query
_embeddings = None
_vectorstore = None

def get_embeddings() -> HuggingFaceBgeEmbeddings:
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embeddings = HuggingFaceBgeEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings

def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        logger.info(f"Connecting to ChromaDB at {CHROMA_PERSIST_DIR}")
        _vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_PERSIST_DIR
        )
    return _vectorstore

def retrieve_context(query: str, top_k: int = RETRIEVER_TOP_K, fund_name: str = None) -> List[Document]:
    """
    Retrieve the top K most relevant chunks for the given query.
    """
    logger.info(f"Retrieving top {top_k} chunks for query: '{query}'")
    vectorstore = get_vectorstore()
    
    # Perform similarity search
    search_kwargs = {"k": top_k}
    if fund_name:
        search_kwargs["filter"] = {"scheme_name": fund_name}
        
    results = vectorstore.similarity_search(query, **search_kwargs)
    logger.info(f"Retrieved {len(results)} chunks.")
    return results
