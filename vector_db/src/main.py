import os
import json
import logging
from vector_db.src import config
from vector_db.src.embedder import LocalEmbedder
from vector_db.src.store import VectorStoreManager

# Setup seeder logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VectorDBSeeder")

def seed_database():
    logger.info("=== Starting Vector Database Seeding (Phase 2) ===")
    
    # 1. Check if input chunk seed file exists
    if not os.path.exists(config.CHUNKS_JSON_PATH):
        logger.error(f"Ingested chunks file not found at {config.CHUNKS_JSON_PATH}. Please run Phase 1 first!")
        return False

    # 2. Read chunks
    logger.info(f"Reading chunks from: {config.CHUNKS_JSON_PATH}")
    with open(config.CHUNKS_JSON_PATH, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    logger.info(f"Loaded {len(chunks)} text chunks.")
    if not chunks:
        logger.warning("No chunks to process. Seeding aborted.")
        return False

    # 3. Load embedding model and calculate vectors
    embedder = LocalEmbedder()
    
    logger.info("Generating embeddings for all chunks (this may take a few seconds)...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedder.embed_documents(texts)
    logger.info("Embeddings generation complete.")

    # 4. Initialize store and upsert data
    store = VectorStoreManager()
    store.upsert_chunks(chunks, embeddings)
    logger.info("Vector database seeding completed successfully!")
    
    # 5. Run a validation query to verify retrieval functionality
    logger.info("--- Step 5: Running Validation Similarity Search ---")
    test_query = "What is the exit load for HDFC Mid-Cap Opportunities Fund?"
    logger.info(f"Query: '{test_query}'")
    
    query_vector = embedder.embed_query(test_query)
    # We can also add a metadata filter to isolate the test to the mid cap fund
    metadata_filter = {"scheme_name": "HDFC Mid-Cap Opportunities Fund"}
    
    results = store.query(query_vector, limit=2, metadata_filter=metadata_filter)
    
    print("\n--- Validation Query Results ---")
    for idx, res in enumerate(results):
        print(f"\nResult #{idx+1}:")
        print(f"  Chunk ID: {res['chunk_id']}")
        print(f"  Scheme:   {res['metadata']['scheme_name']}")
        print(f"  Doc Type: {res['metadata']['document_type']}")
        print(f"  Distance: {res['distance']:.4f}")
        print(f"  Snippet:  {res['text'][:150]}...")
    print("---------------------------------\n")
    
    return True

if __name__ == "__main__":
    seed_database()
