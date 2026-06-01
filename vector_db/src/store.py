import logging
import chromadb
from chromadb.config import Settings
from vector_db.src import config

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self):
        logger.info(f"Initializing persistent ChromaDB client at: {config.DB_PATH}")
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=config.DB_PATH)
        
        # Get or create collection
        # We specify cosine similarity as the distance metric (standard for text retrieval)
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Connected to collection: '{config.COLLECTION_NAME}'")

    def upsert_chunks(self, chunks: list, embeddings: list):
        """
        Upserts a batch of document chunks with their calculated vector embeddings into ChromaDB.
        """
        if not chunks or not embeddings:
            logger.warning("Empty chunks or embeddings. Skipping upsert.")
            return

        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: Got {len(chunks)} chunks and {len(embeddings)} embeddings.")

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["chunk_id"])
            documents.append(chunk["text"])
            
            # Formulate metadata dictionary
            metadata = {
                "scheme_name": chunk["scheme_name"],
                "source_url": chunk["source_url"],
                "document_type": chunk["document_type"],
                "last_updated_date": chunk["last_updated_date"]
            }
            metadatas.append(metadata)

        logger.info(f"Upserting {len(ids)} items into ChromaDB collection...")
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        logger.info("Upsert complete.")

    def query(self, query_vector: list, limit: int = 3, metadata_filter: dict = None) -> list:
        """
        Queries ChromaDB for similar chunks using a query vector and optional metadata filtering.
        """
        logger.info(f"Querying database (limit={limit}, filter={metadata_filter})...")
        
        # Query the database
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
            where=metadata_filter
        )
        
        # Parse output into clean list of dict records
        parsed_results = []
        if results and "ids" in results and results["ids"]:
            # Parallel arrays are returned inside a nested list, get first query result index 0
            ids = results["ids"][0]
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            # ChromaDB returns distance (higher means less similar for cosine in default settings,
            # but custom settings or metric configurations may vary. Let's return the raw distance)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(ids)

            for i in range(len(ids)):
                parsed_results.append({
                    "chunk_id": ids[i],
                    "text": documents[i],
                    "metadata": metadatas[i],
                    "distance": distances[i]
                })

        logger.info(f"Found {len(parsed_results)} matching chunks.")
        return parsed_results
