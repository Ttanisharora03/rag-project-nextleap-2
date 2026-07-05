import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.config import GROQ_API_KEY, LLM_MODEL
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

def test():
    print(f"Testing Groq LLM integration...")
    print(f"Model: {LLM_MODEL}")
    
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        print("ERROR: GROQ_API_KEY is missing or not configured correctly in .env.")
        return
        
    print("Initializing ChatGroq...")
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0.0,
        max_tokens=50
    )
    
    print("Sending test message to Groq API...")
    try:
        response = llm.invoke([HumanMessage(content="Hello! Please reply with exactly: 'LLM is working perfectly.'")])
        print("\nResponse received:")
        print("-" * 40)
        print(response.content)
        print("-" * 40)
        print("\nTest completed successfully!")
    except Exception as e:
        print(f"\nERROR occurred while calling Groq API: {e}")

if __name__ == "__main__":
    test()
