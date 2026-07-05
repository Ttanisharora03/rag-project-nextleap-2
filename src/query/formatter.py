"""
Response formatter module.
Post-processes the LLM response to ensure it adheres to length and formatting rules.
"""
import re
from datetime import datetime

def format_response(response: str) -> str:
    """
    Format and validate the LLM response.
    Ensures length constraints and footer presence.
    """
    # Simple heuristic to trim response to max 3 sentences if it hallucinated more.
    # Note: We rely heavily on the LLM prompt to restrict length, but this is a fallback.
    sentences = re.split(r'(?<=[.!?])\s+', response.strip())
    
    # We want to preserve the footer if it exists.
    # Let's check if the footer is present.
    footer_pattern = re.compile(r'(Last updated from sources:.*?$)', re.IGNORECASE | re.DOTALL)
    match = footer_pattern.search(response)
    
    footer = ""
    main_text = response
    if match:
        footer = match.group(1)
        main_text = response.replace(footer, "").strip()
        
    main_sentences = re.split(r'(?<=[.!?])\s+', main_text)
    
    if len(main_sentences) > 3:
        main_text = " ".join(main_sentences[:3])
        
    final_response = main_text
    
    if footer:
        if not final_response.endswith("\n\n"):
            final_response += "\n\n"
        final_response += footer
    else:
        # Inject today's date if LLM missed the footer completely
        today = datetime.now().strftime("%Y-%m-%d")
        final_response += f"\n\nLast updated from sources: {today}"
        
    return final_response
