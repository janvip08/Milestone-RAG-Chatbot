# Phase 3: Query Processing & Refusal Guardrails

This directory contains the code to scan, compliance-check, and route incoming user queries before they hit the vector database or LLM generator.

## Components

- `src/config.py`: Regex constants for Aadhaar/PAN/Phone/Email/Accounts, polite refusal templates, AMFI/SEBI educational links.
- `src/pii_filter.py`: Checks for critical PII (Aadhaar, PAN, Bank Accounts, OTP codes) and blocks them. Masks non-critical PII (Emails, Phone numbers).
- `src/intent_classifier.py`: Routes queries into `FACTUAL`, `ADVISORY`, or `PERFORMANCE` using compiled keyword patterns. Extracts target scheme name to route search scope.
- `src/refusal_handler.py`: Standardizes compliance responses (pointing to AMFI or the official factsheet depending on query type).
- `src/main.py`: Entry point coordinating all checks and running the validation test suite.

## How to Run the Test Suite

Run the guardrail validator from the workspace root:
```powershell
$env:PYTHONPATH="c:\Users\Abhishek kapoor\RAG"
python query_processing/src/main.py
```
