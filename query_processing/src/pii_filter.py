import re
import logging
from query_processing.src import config

logger = logging.getLogger(__name__)

# Pattern for OTP: 4 to 6 digit numbers
OTP_CANDIDATE = re.compile(r'\b\d{4,6}\b')
OTP_KEYWORDS = [r'otp', r'pin', r'code', r'password', r'verification', r'one time']

def has_otp_context(query: str) -> bool:
    """
    Checks if a query contains a numeric block of 4-6 digits along with OTP-related keywords.
    """
    query_lower = query.lower()
    if OTP_CANDIDATE.search(query):
        for keyword in OTP_KEYWORDS:
            if re.search(r'\b' + keyword, query_lower):
                return True
    return False

def scan_and_mask_pii(query: str) -> tuple:
    """
    Scans a query for Aadhaar, PAN, bank account numbers, OTPs, emails, and phone numbers.
    
    If critical PII (Aadhaar, PAN, Account Numbers, OTPs) is detected:
        returns (is_blocked=True, response_message=config.PII_REJECTION_MESSAGE, cleaned_query=query)
        
    If non-critical PII (Email, Phone Numbers) is detected:
        masks the values (e.g., [EMAIL], [PHONE]) and returns (is_blocked=False, response_message=None, cleaned_query=masked_query)
    """
    cleaned_query = query
    is_blocked = False

    # 1. Check for Aadhaar Card
    if config.AADHAAR_PATTERN.search(query):
        logger.warning("PII Filter Triggered: Aadhaar card detected in query.")
        is_blocked = True
        return is_blocked, config.PII_REJECTION_MESSAGE, query

    # 2. Check for PAN Card
    if config.PAN_PATTERN.search(query):
        logger.warning("PII Filter Triggered: PAN card detected in query.")
        is_blocked = True
        return is_blocked, config.PII_REJECTION_MESSAGE, query

    # 3. Check for OTP / Verification codes
    if has_otp_context(query):
        logger.warning("PII Filter Triggered: Potential OTP/verification code detected in query.")
        is_blocked = True
        return is_blocked, config.PII_REJECTION_MESSAGE, query

    # 4. Mask Phone Numbers (non-blocking, do this before bank account check so 10-digit phones don't trigger it)
    if config.PHONE_PATTERN.search(cleaned_query):
        logger.info("PII Filter: Phone number detected. Masking phone number...")
        cleaned_query = config.PHONE_PATTERN.sub("[PHONE]", cleaned_query)

    # 5. Mask Emails (non-blocking, do this before bank account check)
    if config.EMAIL_PATTERN.search(cleaned_query):
        logger.info("PII Filter: Email address detected. Masking email address...")
        cleaned_query = config.EMAIL_PATTERN.sub("[EMAIL]", cleaned_query)

    # 6. Check for Bank Accounts (consecutive digits 9 to 18, evaluated on cleaned/masked query)
    if config.ACCOUNT_PATTERN.search(cleaned_query):
        logger.warning("PII Filter Triggered: Bank account or card number detected in query.")
        is_blocked = True
        return is_blocked, config.PII_REJECTION_MESSAGE, query

    return is_blocked, None, cleaned_query
