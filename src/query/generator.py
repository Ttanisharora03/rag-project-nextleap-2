"""
LLM Generator module.
Takes retrieved context and user query, formats them into a strict prompt,
and calls the Groq LLM to generate a factual response.
"""
import logging
import time
from typing import List

# pyrefly: ignore [missing-import]
from langchain_core.documents import Document
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate

from src.config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from src.query.rate_limiter import rate_limiter, estimate_tokens, RateLimitException

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a facts-only mutual fund FAQ assistant for ICICI Prudential schemes.

RULES:
1. Answer ONLY using the provided context. Do NOT use external knowledge.
2. Limit responses to a MAXIMUM of 3 sentences.
3. Include EXACTLY ONE source citation link in your response.
4. End every response with: "Last updated from sources: <date>" (use the scrape_date from context metadata, or today's date if missing).
5. NEVER provide investment advice, opinions, or recommendations.
6. NEVER compare fund performance or calculate returns.
7. If the question is advisory, refuse politely and provide an educational link.
8. If the answer is not in the context, say "I don't have this information in my sources."

CONTEXT:
{context}
"""

_llm = None

def get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        logger.info(f"Initializing Groq LLM: {LLM_MODEL}")
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY is missing or not configured correctly.")
            
        _llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
    return _llm

def generate_response(query: str, chunks: List[Document]) -> str:
    """
    Generate a response using Groq based on the retrieved chunks.
    """
    logger.info("Formatting context for generation...")
    
    # Format chunks into a single context string with metadata
    context_parts = []
    latest_date = None
    for chunk in chunks:
        source = chunk.metadata.get("source_url", "Unknown source")
        date = chunk.metadata.get("scrape_date", "Unknown date")
        if latest_date is None or (date != "Unknown date" and date > latest_date):
            latest_date = date
            
        context_parts.append(f"Content:\n{chunk.page_content}\nSource: {source}\nScraped: {date}\n---")
        
    context_str = "\n".join(context_parts)
    
    # Pre-flight Rate Limit Check
    full_prompt_text = SYSTEM_PROMPT + "\n" + context_str + "\n" + query
    est_tokens = estimate_tokens(full_prompt_text)
    
    is_allowed, block_reason = rate_limiter.check_limits(est_tokens)
    if not is_allowed:
        logger.warning(f"Rate limiter blocked request: {block_reason}")
        raise RateLimitException(block_reason)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{query}")
    ])
    
    chain = prompt | get_llm()
    
    logger.info("Invoking LLM...")
    
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            response = chain.invoke({
                "context": context_str,
                "query": query
            })
            
            # Record actual usage if available, else fallback to est_tokens
            actual_tokens = est_tokens
            if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
                actual_tokens = response.response_metadata['token_usage'].get('total_tokens', est_tokens)
            
            rate_limiter.record_usage(actual_tokens)
            
            logger.info("LLM generation complete.")
            return response.content
            
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(f"Groq API rate limit hit. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded for rate limit.")
                    raise RateLimitException("Service is temporarily busy. Please try again in a moment.")
            else:
                logger.error(f"LLM generation failed: {e}")
                raise Exception("I couldn't generate a response. Please try rephrasing your question.")
