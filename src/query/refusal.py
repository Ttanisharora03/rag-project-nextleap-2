"""
Refusal handler module.
Returns static polite refusal templates based on classification.
"""

def get_refusal_response(classification: str) -> str:
    """
    Returns the appropriate refusal response for a given classification.
    """
    if classification == "ADVISORY":
        return "I'm a facts-only assistant and cannot provide investment advice. For guidance, visit https://www.amfiindia.com/ or consult a SEBI-registered advisor."
    elif classification == "PII_DETECTED":
        return "For your security, please do not share personal information like PAN, Aadhaar, or account numbers here."
    elif classification == "OFF_TOPIC":
        return "I can only answer factual questions about ICICI Prudential mutual fund schemes."
        
    return "I cannot answer this question."
