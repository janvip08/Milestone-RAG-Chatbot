# Phase 4: Retrieval-Augmented Generation (RAG) Core

This directory implements the core RAG orchestration logic using local embeddings, persistent ChromaDB filtering, and the Groq API for generation.

## Components

- `src/config.py`: Credentials (via `.env`), temperature, system prompt guidelines.
- `src/retriever.py`: Vector search with schema isolation filters.
- `src/generator.py`: Groq API completion wrapper (with a Mock LLM local fallback).
- `src/synthesizer.py`: Formats citations and suppresses URLs on refusals.
- `src/main.py`: Coordinates the end-to-end RAG workflow (incorporating Phase 3 guardrails).

## How to Run

Run the end-to-end RAG pipeline validator from the workspace root:
```powershell
$env:PYTHONPATH="c:\Users\Abhishek kapoor\RAG"
python rag_core/src/main.py
```
