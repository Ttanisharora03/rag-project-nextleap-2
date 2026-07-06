"""
Query Pipeline (RAG Core) entry point.
"""
import logging

from src.query.classifier import classify_query
from src.query.refusal import get_refusal_response
from src.query.retriever import retrieve_context
from src.query.generator import generate_response
from src.query.formatter import format_response
from src.query.rate_limiter import RateLimitException

logger = logging.getLogger(__name__)

def query_rag(user_query: str, fund_name: str = None) -> dict:
    """
    End-to-end RAG pipeline for a user query.
    1. Classify
    2. Guardrails (Refusal)
    3. Retrieve
    4. Generate
    5. Format
    """
    logger.info(f"Processing query: '{user_query}'")
    
    # 1. Classification
    classification = classify_query(user_query)
    
    # 2. Refusal Guardrails
    if classification != "FACTUAL":
        refusal_msg = get_refusal_response(classification)
        return {
            "answer": refusal_msg,
            "type": "refusal",
            "classification": classification
        }
        
    # 3. Retrieve Context
    chunks = retrieve_context(user_query, fund_name=fund_name)
    if not chunks:
        return {
            "answer": "I don't have this information in my sources.",
            "type": "factual",
            "classification": "FACTUAL"
        }
        
    # 4. Generate Response
    try:
        raw_response = generate_response(user_query, chunks)
    except RateLimitException as e:
        return {
            "answer": str(e),
            "type": "error",
            "classification": "FACTUAL"
        }
    except Exception as e:
        logger.error(f"Error in RAG generation: {e}")
        return {
            "answer": "I couldn't generate a response. Please try rephrasing your question.",
            "type": "error",
            "classification": "FACTUAL"
        }
    
    # 5. Format Response
    final_response = format_response(raw_response)
    
    return {
        "answer": final_response,
        "type": "factual",
        "classification": "FACTUAL"
    }
