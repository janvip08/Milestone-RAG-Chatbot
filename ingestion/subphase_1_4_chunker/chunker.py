import os
import re
import json
import logging
from ingestion.subphase_1_1_registry import config

logger = logging.getLogger(__name__)

def split_text_semantically(text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> list:
    """
    Splits text into overlapping chunks, attempting to respect sentence boundaries.
    """
    # Split text into sentences using simple lookbehind regex
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_len = len(sentence)
        
        # If a single sentence is larger than the chunk size limit, split it by words
        if sentence_len > chunk_size:
            # Commit the current chunk if it exists
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            
            words = sentence.split(' ')
            sub_chunk = []
            sub_len = 0
            for word in words:
                word_len = len(word)
                if sub_len + word_len + (1 if sub_chunk else 0) > chunk_size:
                    if sub_chunk:
                        chunks.append(" ".join(sub_chunk))
                        # Create overlap by keeping a few trailing words
                        words_to_keep = max(1, int(overlap / 8))
                        sub_chunk = sub_chunk[-words_to_keep:] + [word]
                        sub_len = sum(len(w) for w in sub_chunk) + len(sub_chunk) - 1
                    else:
                        chunks.append(word)
                        sub_chunk = []
                        sub_len = 0
                else:
                    sub_chunk.append(word)
                    sub_len += word_len + (1 if len(sub_chunk) > 1 else 0)
            if sub_chunk:
                chunks.append(" ".join(sub_chunk))
            continue
            
        # Standard case: If adding sentence exceeds chunk_size, commit and backtrack for overlap
        if current_length + sentence_len + (1 if current_chunk else 0) > chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                
                # Backtrack to build the overlap segment
                overlap_sentences = []
                overlap_len = 0
                for sent in reversed(current_chunk):
                    sent_len = len(sent)
                    if overlap_len + sent_len + (1 if overlap_sentences else 0) <= overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_len += sent_len + (1 if len(overlap_sentences) > 1 else 0)
                    else:
                        break
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk) + len(current_chunk) - 1
            else:
                current_chunk = [sentence]
                current_length = sentence_len
        else:
            current_chunk.append(sentence)
            current_length += sentence_len + (1 if len(current_chunk) > 1 else 0)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def chunk_cleaned_file(json_filepath: str) -> list:
    """
    Reads a cleaned JSON file, splits its text into chunks, and attaches metadata to each.
    """
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            doc_record = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read cleaned file {json_filepath}: {str(e)}")
        return []

    scheme_name = doc_record.get("scheme_name", "Unknown")
    source_url = doc_record.get("source_url", "")
    doc_type = doc_record.get("document_type", "")
    last_updated_date = doc_record.get("last_updated_date", "")
    text = doc_record.get("cleaned_text", "")
    
    if not text:
        return []
        
    base_filename = os.path.splitext(os.path.basename(json_filepath))[0].replace("_cleaned", "")
    text_chunks = split_text_semantically(text)
    
    chunks_with_metadata = []
    for idx, chunk_text in enumerate(text_chunks):
        chunk_record = {
            "chunk_id": f"{base_filename}_chunk_{idx}",
            "scheme_name": scheme_name,
            "source_url": source_url,
            "document_type": doc_type,
            "last_updated_date": last_updated_date,
            "text": chunk_text
        }
        chunks_with_metadata.append(chunk_record)
        
    logger.info(f"Chunked {base_filename}: Split into {len(chunks_with_metadata)} chunks.")
    return chunks_with_metadata

def run_chunker(cleaned_filepaths: list) -> str:
    """
    Processes all cleaned documents, generates chunks, and writes a single aggregated chunks.json.
    """
    logger.info("Starting Phase 1 Chunker...")
    all_chunks = []
    
    for filepath in cleaned_filepaths:
        doc_chunks = chunk_cleaned_file(filepath)
        all_chunks.extend(doc_chunks)
        
    dest_path = os.path.join(config.CHUNKS_DIR, "chunks.json")
    try:
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=4, ensure_ascii=False)
        logger.info(f"Chunker finished. Saved {len(all_chunks)} chunks to {dest_path}")
        return dest_path
    except Exception as e:
        logger.error(f"Failed to save chunks to {dest_path}: {str(e)}")
        return None

if __name__ == "__main__":
    pass
