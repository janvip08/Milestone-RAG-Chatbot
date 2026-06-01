import os
import time
import shutil
import requests
import logging
from ingestion.subphase_1_1_registry import config

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

def download_source(url: str, filename: str, doc_type: str, use_mock: bool = config.USE_MOCK_FALLBACK) -> str:
    """
    Downloads a document from a URL and saves it to the raw data directory.
    If use_mock is True, or if the download fails (e.g., due to 403 Forbidden/anti-scraping),
    it will fall back to copying the pre-configured mock file.
    
    Returns the path to the saved raw file, or None if it fails completely.
    """
    dest_path = os.path.join(config.RAW_DIR, filename)
    mock_source_path = os.path.join(config.MOCK_DIR, filename)
    
    # 1. Mock Mode (Fallback to local mock data to guarantee execution)
    if use_mock:
        logger.info(f"[Mock Mode] Loading {filename} from mock registry.")
        if os.path.exists(mock_source_path):
            shutil.copy(mock_source_path, dest_path)
            logger.info(f"Successfully copied mock data to {dest_path}")
            return dest_path
        else:
            logger.error(f"Mock file not found at {mock_source_path}")
            # fall through to live download if mock file is missing
            logger.info("Attempting live download as fallback...")

    # 2. Live Downloading Mode
    logger.info(f"Attempting download of {url} -> {dest_path}")
    try:
        # Respectful delay before download
        time.sleep(config.SCRAPE_DELAY)
        
        response = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        if response.status_code == 200:
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.info(f"Successfully downloaded and saved: {dest_path}")
            return dest_path
        else:
            logger.warning(f"Failed to download {url}. HTTP Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")

    # 3. Fallback to mock if live request failed and we haven't already tried it
    if not use_mock:
        logger.warning(f"Live download failed for {url}. Attempting mock fallback...")
        if os.path.exists(mock_source_path):
            shutil.copy(mock_source_path, dest_path)
            logger.info(f"Successfully copied mock data to {dest_path} (Fallback)")
            return dest_path
        else:
            logger.error(f"Mock fallback failed: Mock file not found at {mock_source_path}")

    return None

def run_scraper():
    """
    Orchestrates the downloading of all registered schemes and general sources.
    """
    logger.info("Starting Phase 1 Scraper & Document Loader...")
    downloaded_files = []

    # Process individual schemes
    for scheme in config.SCHEMES:
        logger.info(f"Processing scheme: {scheme['name']}")
        for src in scheme["official_sources"]:
            dest = download_source(src["url"], src["filename"], src["doc_type"])
            if dest:
                downloaded_files.append((dest, scheme["name"], src["doc_type"], src["url"]))

    # Process general sources
    for src in config.GENERAL_SOURCES:
        logger.info(f"Processing general source: {src['name']}")
        dest = download_source(src["url"], src["filename"], src["doc_type"])
        if dest:
            downloaded_files.append((dest, "General", src["doc_type"], src["url"]))

    logger.info(f"Scraper finished. Total files loaded to raw storage: {len(downloaded_files)}")
    return downloaded_files

if __name__ == "__main__":
    run_scraper()
