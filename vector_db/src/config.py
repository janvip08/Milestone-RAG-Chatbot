import os

# Project Path Setup
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_ROOT = os.path.dirname(SRC_DIR)
WORKSPACE_ROOT = os.path.dirname(PHASE2_ROOT)

# Paths
DB_PATH = os.path.join(PHASE2_ROOT, "data", "db")
CHUNKS_JSON_PATH = os.path.join(WORKSPACE_ROOT, "ingestion", "subphase_1_4_chunker", "data", "chunks", "chunks.json")

# Ensure DB folder exists
os.makedirs(DB_PATH, exist_ok=True)

# Settings
MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "mutual_fund_facts"
