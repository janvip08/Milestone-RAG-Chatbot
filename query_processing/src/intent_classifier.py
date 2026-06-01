import re
import logging
from query_processing.src import config

logger = logging.getLogger(__name__)

# Compile patterns for Advisory queries
ADVISORY_PATTERNS = [
    r'\bshould\s+i\s+invest\b',
    r'\bwhich\s+is\s+better\b',
    r'\bbest\s+fund\b',
    r'\brecommend\b',
    r'\badvice\b',
    r'\bsuggest\b',
    r'\bcompare\b',
    r'\bbetter\s+choice\b',
    r'\bbuy\s+or\s+sell\b',
    r'\bis\s+it\s+good\b',
    r'\bwhich\s+one\s+to\s+choose\b',
    r'\bworth\s+investing\b',
    r'\bhow\s+should\s+i\s+plan\b'
]

# Compile patterns for Performance / Return calculation queries
PERFORMANCE_PATTERNS = [
    r'\breturns\b',
    r'\bcagr\b',
    r'\bannualized\b',
    r'\bcalculate\s+(?:.*\s+)?returns\b',
    r'\bhow\s+much\s+money\s+will\s+i\s+make\b',
    r'\bperformance\b',
    r'\bpast\s+returns\b',
    r'\byield\b',
    r'\bcalculate\s+sip\b',
    r'\bprofit\b'
]

def classify_intent(query: str) -> str:
    """
    Classifies the user query intent as ADVISORY, PERFORMANCE, or FACTUAL.
    """
    query_lower = query.lower()

    # 1. Check for Advisory intent
    for pattern in ADVISORY_PATTERNS:
        if re.search(pattern, query_lower):
            logger.info(f"Intent Classification: Triggered ADVISORY guardrail pattern: '{pattern}'")
            return "ADVISORY"

    # 2. Check for Performance / Return calculations intent
    for pattern in PERFORMANCE_PATTERNS:
        if re.search(pattern, query_lower):
            logger.info(f"Intent Classification: Triggered PERFORMANCE guardrail pattern: '{pattern}'")
            return "PERFORMANCE"

    # 3. Default to Factual
    logger.info("Intent Classification: Classified as FACTUAL query.")
    return "FACTUAL"

def extract_scheme_context(query: str) -> str:
    """
    Scans the query to match scheme aliases. 
    Returns the official full name of the matching scheme, or 'General' if no scheme matches.
    """
    query_lower = query.lower()
    
    for official_name, scheme_info in config.SCHEME_MAPPINGS.items():
        for alias in scheme_info["aliases"]:
            # Check for exact word boundaries or sub-phrases
            if re.search(r'\b' + re.escape(alias) + r'\b', query_lower):
                logger.info(f"Scheme Context: Matched alias '{alias}' -> Scheme: '{official_name}'")
                return official_name

    logger.info("Scheme Context: No specific scheme matched. Defaulting to 'General'.")
    return "General"
