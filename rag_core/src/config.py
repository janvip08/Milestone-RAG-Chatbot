import os
from dotenv import load_dotenv

# Project Path Setup
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE4_ROOT = os.path.dirname(SRC_DIR)
WORKSPACE_ROOT = os.path.dirname(PHASE4_ROOT)

# Load env variables (e.g. from RAG/.env if it exists)
load_dotenv(os.path.join(WORKSPACE_ROOT, ".env"), override=True)

# Groq Credentials & Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0.0

# Search Settings
TOP_K_CHUNKS = 3

# System Prompt Rules
SYSTEM_PROMPT = (
    "You are a compliant facts-only Mutual Fund FAQ Assistant.\n"
    "Your job is to answer the user query using ONLY the provided context blocks.\n"
    "Strictly follow these rules:\n"
    "1. Answer using ONLY the provided context. If the context does not contain the answer, "
    "you MUST reply exactly with: 'I do not have enough information to answer this query.'\n"
    "2. Do NOT use any pre-trained or outside knowledge. Do NOT speculate, extrapolate, or assume.\n"
    "3. Limit your answer to a maximum of 3 sentences.\n"
    "4. Do NOT provide investment advice, recommendations, opinions, or performance comparisons.\n"
    "5. Keep the tone completely objective, neutral, and matter-of-fact."
)
