import logging
from query_processing.src.main import process_user_query
from rag_core.src.retriever import retrieve_context
from rag_core.src.generator import generate_answer
from rag_core.src.synthesizer import synthesize_response

# Configure main RAG pipeline logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("RAGPipeline")

def run_rag_pipeline(query: str) -> str:
    """
    Executes the end-to-end RAG pipeline:
    Query -> Compliance/PII Check -> Vector DB Retrieval -> LLM Generation -> Output Synthesis.
    """
    logger.info(f"RAG Pipeline: Processing incoming query: '{query}'")

    # 1. Guardrail checks (Phase 3)
    guardrail_result = process_user_query(query)
    
    if guardrail_result["status"] in ["BLOCKED_PII", "REJECTED_COMPLIANCE"]:
        logger.warning(f"RAG Pipeline: Query rejected at guardrail stage ({guardrail_result['status']})")
        # Returns the compliant warning/refusal response directly
        return guardrail_result["response"]

    # Approved query (Factual)
    clean_query = guardrail_result["clean_query"]
    scheme_context = guardrail_result["scheme_context"]

    # 2. Retrieve Context Chunks (Phase 2)
    chunks = retrieve_context(clean_query, scheme_context)

    # 3. Generate completion (Phase 4)
    raw_answer = generate_answer(clean_query, chunks)

    # 4. Format & Synthesize Output (Phase 4 Synthesizer)
    final_response = synthesize_response(raw_answer, chunks)
    
    logger.info("RAG Pipeline: Output successfully synthesized.")
    return final_response

def run_rag_test_suite():
    print("\n==================================================")
    print("      RUNNING END-TO-END RAG PIPELINE TEST        ")
    print("==================================================")
    
    test_cases = [
        # Case 1: PII Blocked Query
        "My Aadhaar is 5544-3322-1100. Tell me the SIP limit for Mid-Cap.",
        
        # Case 2: Advisory Blocked Query
        "Should I invest in HDFC Large Cap Fund or ELSS?",
        
        # Case 3: Specific Scheme Factual Query (Mid-Cap Exit Load)
        "What is the exit load for HDFC Mid-Cap Opportunities Fund?",
        
        # Case 4: Specific Scheme Factual Query (ELSS Lock-in)
        "What is the lock-in period for HDFC ELSS Tax Saver Fund?",
        
        # Case 5: General Factual Query (FAQ Statement Guide)
        "How can I download my capital gains statement?",
        
        # Case 6: Unregistered Scheme / Factual Refusal (Tests unknown query - no URL)
        "What is the minimum investment for HDFC Gold Fund?"
    ]
    
    for idx, query in enumerate(test_cases):
        print(f"\n[Test Case #{idx+1}]")
        print(f"Query:  '{query}'")
        response = run_rag_pipeline(query)
        print("Response:")
        print(response)
        print("-" * 50)

if __name__ == "__main__":
    run_rag_test_suite()
