"""
Centralized configuration module for the Mutual Fund FAQ Assistant.

Loads all settings from environment variables (via .env file) and exposes
them as typed constants for use across the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from the project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Groq API (LLM Provider)
# ---------------------------------------------------------------------------
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# ---------------------------------------------------------------------------
# Model Settings
# ---------------------------------------------------------------------------
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "200"))

# ---------------------------------------------------------------------------
# ChromaDB / Vector Store
# ---------------------------------------------------------------------------
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "icici_prudential_mf_corpus")
CHROMA_PERSIST_DIR: str = os.getenv(
    "CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "vectorstore")
)

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
RETRIEVER_TOP_K: int = int(os.getenv("RETRIEVER_TOP_K", "5"))

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
URLS_FILE: Path = DATA_DIR / "urls.json"
FRONTEND_DIR: Path = PROJECT_ROOT / "frontend"


def validate_config() -> dict[str, bool]:
    """
    Validate that all critical configuration values are set.

    Returns a dict mapping config names to whether they are valid.
    """
    checks = {
        "GROQ_API_KEY": bool(GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here"),
        "EMBEDDING_MODEL": bool(EMBEDDING_MODEL),
        "LLM_MODEL": bool(LLM_MODEL),
        "CHROMA_COLLECTION": bool(CHROMA_COLLECTION),
        "CHROMA_PERSIST_DIR": bool(CHROMA_PERSIST_DIR),
    }
    return checks


if __name__ == "__main__":
    # Quick sanity check when run directly
    print("=" * 60)
    print("Mutual Fund FAQ Assistant — Configuration Check")
    print("=" * 60)
    results = validate_config()
    all_ok = True
    for name, ok in results.items():
        status = "[OK]" if ok else "[MISSING]"
        print(f"  {status}  {name}")
        if not ok:
            all_ok = False
    print("-" * 60)
    if all_ok:
        print("All configuration values loaded successfully.")
    else:
        print("WARNING: Some configuration values are missing or invalid.")
        print("Please check your .env file.")
    print(f"\n  Project root : {PROJECT_ROOT}")
    print(f"  Data dir     : {DATA_DIR}")
    print(f"  Vector store : {CHROMA_PERSIST_DIR}")
    print(f"  LLM model    : {LLM_MODEL}")
    print(f"  Embed model  : {EMBEDDING_MODEL}")
