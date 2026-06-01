import logging
from sentence_transformers import SentenceTransformer
from vector_db.src import config

logger = logging.getLogger(__name__)

class LocalEmbedder:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(LocalEmbedder, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        logger.info(f"Loading local embedding model: {config.MODEL_NAME}...")
        # SentenceTransformer handles downloading and caching the model locally
        self.model = SentenceTransformer(config.MODEL_NAME)
        logger.info("Embedding model loaded successfully.")
        self._initialized = True

    def embed_query(self, query: str) -> list:
        """
        Generates embedding vector for a user query.
        """
        embedding = self.model.encode(query, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, documents: list) -> list:
        """
        Generates embedding vectors for a list of document text chunks.
        """
        embeddings = self.model.encode(documents, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.tolist()
