import logging
from query_processing.src import config

logger = logging.getLogger(__name__)

def get_refusal_response(intent: str, scheme_name: str) -> str:
    """
    Generates polite and compliance-adherent refusal responses based on the query intent.
    """
    if intent == "ADVISORY":
        logger.info("Refusal Handler: Generating ADVISORY refusal message.")
        return config.ADVISORY_REJECTION_MESSAGE

    elif intent == "PERFORMANCE":
        logger.info(f"Refusal Handler: Generating PERFORMANCE refusal message for scheme '{scheme_name}'.")
        # Lookup scheme to get factsheet URL
        scheme_info = config.SCHEME_MAPPINGS.get(scheme_name)
        
        if scheme_info and scheme_name != "General":
            return config.PERFORMANCE_REJECTION_TEMPLATE.format(
                scheme_name=scheme_name,
                factsheet_url=scheme_info["factsheet_url"]
            )
        else:
            # Generic performance fallback without any URLs if scheme is unknown
            return (
                "Compliance Notification: I cannot calculate returns or perform evaluative comparative performance calculations. "
                "Please refer directly to the official factsheet of the respective scheme for details."
            )
            
    return "Query parsed successfully."
