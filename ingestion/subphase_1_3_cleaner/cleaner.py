import os
import re
import json
import logging
from bs4 import BeautifulSoup
import pypdf
from ingestion.subphase_1_1_registry import config

logger = logging.getLogger(__name__)

def parse_html(file_path: str) -> str:
    """
    Parses HTML file, strips styling/script/nav/footer boilerplate, and returns clean text.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove navigation, scripts, styles, header, footers
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
            
        # Also target common sidebar/header ids/classes
        for element in soup.find_all(id=re.compile(r'(header|footer|sidebar|nav|menu)', re.I)):
            element.decompose()
        for element in soup.find_all(class_=re.compile(r'(header|footer|sidebar|navigation|menu)', re.I)):
            element.decompose()

        # Extract text and replace multiple newlines/spaces with single ones
        text = soup.get_text(separator=' ')
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        logger.error(f"Error parsing HTML file {file_path}: {str(e)}")
        return ""

def parse_pdf(file_path: str) -> str:
    """
    Parses PDF file using pypdf and extracts all readable text.
    """
    try:
        reader = pypdf.PdfReader(file_path)
        text_list = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_list.append(page_text)
        
        full_text = " ".join(text_list)
        # Clean whitespaces
        full_text = re.sub(r'\s+', ' ', full_text).strip()
        return full_text
    except Exception as e:
        logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
        return ""

def extract_last_updated_date(text: str) -> str:
    """
    Heuristically extracts a 'last updated' date from the document text.
    Falls back to a default date if none found.
    """
    # Look for patterns like: "Last updated from sources: May 15, 2026", "As of April 30, 2026", "Last updated: May 2026"
    date_patterns = [
        r"(?:last updated from sources|last updated)\s*[:\-]?\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"(?:as of)\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        r"(?:last updated)\s*[:\-]?\s*([A-Za-z]+\s+\d{4})",
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})"
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
    return "May 30, 2026"  # Default fallback to current time context

def clean_and_extract_metadata(raw_filepath: str, scheme_name: str, doc_type: str, source_url: str) -> str:
    """
    Cleans raw document, extracts metadata, and saves a structured JSON file.
    
    Returns the path to the cleaned JSON file.
    """
    filename = os.path.basename(raw_filepath)
    clean_filename = os.path.splitext(filename)[0] + "_cleaned.json"
    dest_path = os.path.join(config.CLEANED_DIR, clean_filename)
    
    logger.info(f"Cleaning {filename} ({doc_type})...")
    
    # 1. Parse text based on file type
    if raw_filepath.lower().endswith(".html") or raw_filepath.lower().endswith(".htm"):
        cleaned_text = parse_html(raw_filepath)
    elif raw_filepath.lower().endswith(".pdf"):
        cleaned_text = parse_pdf(raw_filepath)
    else:
        # Fallback raw reading
        try:
            with open(raw_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                cleaned_text = re.sub(r'\s+', ' ', f.read()).strip()
        except Exception:
            cleaned_text = ""

    if not cleaned_text:
        logger.warning(f"No text extracted from {raw_filepath}")
        return None

    # 2. Extract last updated date metadata
    last_updated_date = extract_last_updated_date(cleaned_text)
    
    # 3. Create document record
    doc_record = {
        "scheme_name": scheme_name,
        "source_url": source_url,
        "document_type": doc_type,
        "last_updated_date": last_updated_date,
        "cleaned_text": cleaned_text
    }
    
    # 4. Save to JSON
    try:
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(doc_record, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully cleaned and saved metadata: {dest_path}")
        return dest_path
    except Exception as e:
        logger.error(f"Failed to write cleaned file {dest_path}: {str(e)}")
        return None

def run_cleaner(downloaded_files):
    """
    Cleans all downloaded files and writes JSON files with metadata.
    """
    logger.info("Starting Phase 1 Cleaner & Parser...")
    cleaned_files = []
    
    for filepath, scheme_name, doc_type, source_url in downloaded_files:
        clean_path = clean_and_extract_metadata(filepath, scheme_name, doc_type, source_url)
        if clean_path:
            cleaned_files.append(clean_path)
            
    logger.info(f"Cleaner finished. Total files processed: {len(cleaned_files)}")
    return cleaned_files

if __name__ == "__main__":
    pass
