import logging
from query_processing.src.pii_filter import scan_and_mask_pii
from query_processing.src.intent_classifier import classify_intent, extract_scheme_context
from query_processing.src.refusal_handler import get_refusal_response

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("QueryProcessor")

def process_user_query(query: str) -> dict:
    """
    Orchestrates the compliance and security checks on the incoming user query.
    
    Returns a dictionary with status, final response, cleaned query, and metadata schema routing.
    """
    logger.info(f"Processing Query: '{query}'")
    
    # 1. PII Scan & Mask
    is_blocked, pii_response, cleaned_query = scan_and_mask_pii(query)
    if is_blocked:
        logger.warning("Query blocked by PII Guardrail.")
        return {
            "status": "BLOCKED_PII",
            "response": pii_response,
            "clean_query": None,
            "scheme_context": None
        }
        
    # 2. Intent Classification
    intent = classify_intent(cleaned_query)
    
    # 3. Scheme Extraction
    scheme_context = extract_scheme_context(cleaned_query)
    
    # 4. Routing
    if intent in ["ADVISORY", "PERFORMANCE"]:
        logger.warning(f"Query rejected by Compliance Guardrail. Intent: {intent}")
        refusal_msg = get_refusal_response(intent, scheme_context)
        return {
            "status": "REJECTED_COMPLIANCE",
            "response": refusal_msg,
            "clean_query": cleaned_query,
            "scheme_context": scheme_context
        }
        
    # APPROVED - Factual queries
    logger.info(f"Query APPROVED. Target Scheme Context: '{scheme_context}'")
    return {
        "status": "APPROVED",
        "response": None,
        "clean_query": cleaned_query,
        "scheme_context": scheme_context
    }

def run_test_suite():
    print("\n==================================================")
    print("      RUNNING PHASE 3 QUERY GUARDRAILS TEST       ")
    print("==================================================")
    
    test_queries = [
        # 1. Critical PII Block
        ("My PAN is ABCDE1234F. What is the minimum SIP?", "Expected: BLOCKED_PII"),
        
        # 2. OTP Block
        ("Verify my account with OTP 123456", "Expected: BLOCKED_PII"),
        
        # 3. Non-critical PII Masking
        ("Send statements to testuser@gmail.com, my phone is 9988776655.", "Expected: APPROVED (Masked)"),
        
        # 4. Advisory Rejection
        ("Should I invest in HDFC Mid-cap opportunities fund?", "Expected: REJECTED_COMPLIANCE (Advisory)"),
        
        # 5. Performance Rejection
        ("Calculate 5-year returns for HDFC Flexi Cap Fund.", "Expected: REJECTED_COMPLIANCE (Factsheet Redirect)"),
        
        # 6. Approved Factual with Scheme Routing
        ("What is the exit load for HDFC Focused 30?", "Expected: APPROVED (Scheme: HDFC Focused 30 Fund)"),
        
        # 7. Approved General Factual
        ("How can I download my capital gains statement?", "Expected: APPROVED (Scheme: General)"),
        
        # 8. Performance Rejection (Unknown Scheme - No URL expected)
        ("What is the past performance of HDFC Arbitrage Fund?", "Expected: REJECTED_COMPLIANCE (Generic, No URL)")
    ]
    
    for idx, (query, expectation) in enumerate(test_queries):
        print(f"\n[Test #{idx+1}] {expectation}")
        print(f"Input:       '{query}'")
        result = process_user_query(query)
        print(f"Status:      {result['status']}")
        print(f"Context:     {result['scheme_context']}")
        if result['response']:
            print(f"Response:    {result['response']}")
        if result['clean_query'] and result['clean_query'] != query:
            print(f"Clean Query: {result['clean_query']}")
        print("-" * 50)
        
if __name__ == "__main__":
    run_test_suite()
