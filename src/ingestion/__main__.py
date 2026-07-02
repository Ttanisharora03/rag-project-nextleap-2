"""
End-to-end ingestion runner.
Runs the Scraper -> Preprocessor -> Indexer pipeline.
"""
import logging
from src.ingestion.scraper import run_scraper
from src.ingestion.preprocessor import run_preprocessor
from src.ingestion.indexer import run_indexer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("=== Starting Data Ingestion Pipeline ===")
    
    logger.info("--- Step 1: Scraping Data ---")
    run_scraper()
    
    logger.info("--- Step 2: Preprocessing Data ---")
    run_preprocessor()
    
    logger.info("--- Step 3: Indexing Data ---")
    run_indexer()
    
    logger.info("=== Data Ingestion Pipeline Complete ===")

if __name__ == "__main__":
    run_pipeline()
