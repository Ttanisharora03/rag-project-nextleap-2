"""
Query classifier module.
Determines if a query is factual, advisory, off-topic, or contains PII.
"""
import re
import logging

logger = logging.getLogger(__name__)

# PII regex patterns
PAN_PATTERN = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', re.IGNORECASE)
AADHAAR_PATTERN = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_PATTERN = re.compile(r'\b(?:\+91|91)?\s?[6-9]\d{9}\b')

# Advisory keywords
ADVISORY_KEYWORDS = [
    "should i", "recommend", "which is better", "compare", "vs", 
    "good time to invest", "best fund", "top fund", "advice"
]

def classify_query(query: str) -> str:
    """
    Classify the query into: PII_DETECTED, ADVISORY, or FACTUAL.
    """
    logger.info(f"Classifying query: '{query}'")
    
    # 1. Check for PII
    if (PAN_PATTERN.search(query) or 
        AADHAAR_PATTERN.search(query) or 
        EMAIL_PATTERN.search(query) or 
        PHONE_PATTERN.search(query)):
        logger.warning("PII detected in query.")
        return "PII_DETECTED"
        
    # 2. Check for Advisory patterns
    query_lower = query.lower()
    for kw in ADVISORY_KEYWORDS:
        if kw in query_lower:
            logger.warning(f"Advisory keyword '{kw}' detected.")
            return "ADVISORY"
            
    # Note: Off-topic detection is typically harder with just keywords,
    # but we will rely on the LLM's system prompt (Rule 8) to handle it,
    # or implement basic keyword checking if necessary.
    
    logger.info("Query classified as FACTUAL.")
    return "FACTUAL"
