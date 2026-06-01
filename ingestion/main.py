import os
import logging
from ingestion.subphase_1_1_registry import config
from ingestion.subphase_1_2_scraper.scraper import run_scraper
from ingestion.subphase_1_3_cleaner.cleaner import run_cleaner
from ingestion.subphase_1_4_chunker.chunker import run_chunker

# Configure main pipeline logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("Phase1Pipeline")

def main():
    logger.info("=== Starting Mutual Fund FAQ Assistant - Phase 1 Pipeline ===")
    logger.info(f"AMC Target: {config.AMC_NAME}")
    logger.info(f"Mock Mode Active: {config.USE_MOCK_FALLBACK}")
    
    # 1. Scrape / Load Raw Documents
    logger.info("--- Step 1: Scrape / Load Raw Documents ---")
    downloaded_files = run_scraper()
    if not downloaded_files:
        logger.error("No documents loaded/downloaded. Exiting pipeline.")
        return
        
    # 2. Parse & Clean Documents
    logger.info("--- Step 2: Parse & Clean Documents ---")
    cleaned_files = run_cleaner(downloaded_files)
    if not cleaned_files:
        logger.error("No documents cleaned. Exiting pipeline.")
        return
        
    # 3. Chunk Documents
    logger.info("--- Step 3: Semantic Text Chunking ---")
    chunks_path = run_chunker(cleaned_files)
    
    if chunks_path and os.path.exists(chunks_path):
        import json
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
            
        logger.info("=== Phase 1 Pipeline Completed Successfully! ===")
        logger.info(f"Total raw files processed: {len(downloaded_files)}")
        logger.info(f"Total clean files written: {len(cleaned_files)}")
        logger.info(f"Total semantic chunks generated: {len(chunks_data)}")
        logger.info(f"Vector Database Seed File: {chunks_path}")
    else:
        logger.error("Failed to compile final chunk catalog.")

if __name__ == "__main__":
    main()
