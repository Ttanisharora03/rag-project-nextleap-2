import json
import logging
import re
from pathlib import Path
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from src.api.models import ChatRequest, ChatResponse, HealthResponse, SchemesResponse
from src.query import query_rag

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Run the RAG pipeline
        result = query_rag(request.query)
        
        answer = result.get("answer", "")
        response_type = result.get("type", "factual")
        
        # Extract last_updated from the footer
        last_updated = None
        date_match = re.search(r'Last updated from sources: (\d{4}-\d{2}-\d{2})', answer)
        if date_match:
            last_updated = date_match.group(1)
            
        # Extract source URL if present
        source_url = None
        url_match = re.search(r'(https?://[^\s)]+)', answer)
        if url_match:
            source_url = url_match.group(1)
            
        return ChatResponse(
            answer=answer,
            source_url=source_url,
            last_updated=last_updated,
            type=response_type
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", response_model=HealthResponse)
async def health_endpoint():
    return HealthResponse(status="ok")

@router.get("/schemes", response_model=SchemesResponse)
async def schemes_endpoint():
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        urls_file = project_root / "data" / "urls.json"
        with open(urls_file, "r") as f:
            data = json.load(f)
        
        schemes = [item["scheme_name"] for item in data.get("corpus", [])]
        return SchemesResponse(schemes=schemes)
    except Exception as e:
        logger.error(f"Error reading schemes: {e}")
        raise HTTPException(status_code=500, detail="Could not load schemes")
