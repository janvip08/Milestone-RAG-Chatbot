import logging
from rag_core.src import config
from vector_db.src.embedder import LocalEmbedder
from vector_db.src.store import VectorStoreManager

logger = logging.getLogger(__name__)

def retrieve_context(clean_query: str, scheme_context: str) -> list:
    """
    Translates the query to a vector embedding, applies scheme-level metadata isolation,
    and retrieves matching context chunks from ChromaDB.
    """
    logger.info(f"Retriever: Fetching context for query: '{clean_query}' (Context: {scheme_context})")
    
    # 1. Initialize embedder and embed query
    embedder = LocalEmbedder()
    query_vector = embedder.embed_query(clean_query)
    
    # 2. Setup strict scheme isolation filter
    metadata_filter = None
    if scheme_context:
        metadata_filter = {"scheme_name": scheme_context}
        
    # 3. Query the store
    store = VectorStoreManager()
    
    # Log database size diagnostics
    try:
        col_size = store.collection.count()
        logger.info(f"Retriever: Database collection size: {col_size} documents/chunks")
    except Exception as e:
        logger.error(f"Retriever: Failed to get database collection count: {str(e)}")
        col_size = "unknown"

    results = store.query(
        query_vector=query_vector,
        limit=config.TOP_K_CHUNKS,
        metadata_filter=metadata_filter
    )
    
    # Log detailed retrieval results
    logger.info(f"Retriever: Query returned {len(results)} chunks.")
    for idx, res in enumerate(results):
        metadata = res.get("metadata", {})
        source_url = metadata.get("source_url", "N/A")
        distance = res.get("distance", 0.0)
        logger.info(f"  Chunk #{idx+1}: Source={source_url}, Distance/Score={distance:.4f}")
        
    return results
