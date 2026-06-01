import logging
import os
from rag_core.src import config

logger = logging.getLogger(__name__)

# Standard refusal phrases indicating the answer is unknown
REFUSAL_PHRASES = [
    "i do not have enough information",
    "i don't have enough information",
    "i do not have information",
    "i don't have information",
    "unrelated query",
    "context does not mention"
]

# Mapping from external URLs in database to local mock filenames
URL_TO_FILENAME = {
    "https://www.hdfcfund.com/products/hdfc-mid-cap-opportunities-fund": "hdfc_mid_cap.html",
    "https://www.hdfcfund.com/sid/hdfc-mid-cap-opportunities-fund.pdf": "hdfc_mid_cap_sid.pdf",
    "https://www.hdfcfund.com/products/hdfc-flexi-cap-fund": "hdfc_flexi_cap.html",
    "https://www.hdfcfund.com/sid/hdfc-flexi-cap-fund.pdf": "hdfc_flexi_cap_sid.pdf",
    "https://www.hdfcfund.com/products/hdfc-focused-30-fund": "hdfc_focused_30.html",
    "https://www.hdfcfund.com/products/hdfc-elss-tax-saver-fund": "hdfc_elss_tax_saver.html",
    "https://www.hdfcfund.com/products/hdfc-top-100-fund": "hdfc_large_cap.html",
    "https://www.hdfcfund.com/information/faq": "hdfc_faq.html",
    "https://www.amfiindia.com/investor-corner/knowledge-center": "amfi_guidance.html",
}

def is_refusal(answer: str) -> bool:
    """
    Checks if the generated LLM text indicates that it doesn't know the answer.
    """
    ans_lower = answer.lower()
    for phrase in REFUSAL_PHRASES:
        if phrase in ans_lower:
            return True
    return False

def synthesize_response(answer: str, chunks: list) -> str:
    """
    Formats the final response.
    Appends a single source citation link and last updated date footer.
    
    CRITICAL: If the answer is a refusal (e.g., "I do not have enough information..."),
    it does NOT attach any source URLs or citation links.
    """
    if not chunks or is_refusal(answer):
        logger.info("Synthesizer: Response is a refusal. Suppressing source URLs.")
        return answer.strip()

    # Extract metadata from the most relevant chunk (top-1 match)
    top_chunk = chunks[0]
    metadata = top_chunk.get("metadata", {})
    source_url = metadata.get("source_url", "")
    last_updated_date = metadata.get("last_updated_date", "May 30, 2026")

    # Verify and map URL to local /sources/ path
    verified_url = None
    if source_url:
        filename = URL_TO_FILENAME.get(source_url)
        if filename:
            mock_filepath = os.path.join(config.WORKSPACE_ROOT, "ingestion", "subphase_1_1_registry", "data", "mock", filename)
            if os.path.exists(mock_filepath):
                verified_url = f"/sources/{filename}"
                logger.info(f"Synthesizer: Mapped and verified {source_url} -> {verified_url}")
            else:
                logger.warning(f"Synthesizer: Mapped file {mock_filepath} does not exist on disk.")
        elif source_url.startswith("/sources/"):
            filename = source_url.replace("/sources/", "", 1)
            mock_filepath = os.path.join(config.WORKSPACE_ROOT, "ingestion", "subphase_1_1_registry", "data", "mock", filename)
            if os.path.exists(mock_filepath):
                verified_url = source_url
                logger.info(f"Synthesizer: Verified existing local source URL: {verified_url}")
            else:
                logger.warning(f"Synthesizer: Local file {mock_filepath} does not exist on disk.")
        else:
            logger.warning(f"Synthesizer: No mapping found for external source URL: {source_url}")

    # Format output
    final_output = f"{answer.strip()}\n\n"
    if verified_url:
        final_output += f"Source: {verified_url}\n"
    final_output += f"Last updated from sources: {last_updated_date}"

    logger.info("Synthesizer: Appended citation and date footer.")
    return final_output

