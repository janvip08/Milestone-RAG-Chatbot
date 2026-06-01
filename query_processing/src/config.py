import re

# AMFI / SEBI Compliance Links
AMFI_EDUCATIONAL_URL = "https://www.amfiindia.com/investor-corner/knowledge-center"
SEBI_INVESTOR_URL = "https://investor.sebi.gov.in"

# Rejection Messages (Polite & Compliant)
PII_REJECTION_MESSAGE = (
    "Security warning: Your query was rejected because it contains sensitive personal data "
    "(such as Aadhaar, PAN card, email, phone number, or bank details). "
    "To protect your privacy, please re-submit your query without any personal details."
)

ADVISORY_REJECTION_MESSAGE = (
    "Compliance Notification: I can only answer objective, facts-only queries about mutual fund schemes "
    "(e.g., minimum SIP, exit loads, expense ratios, risk ratings, or statement download guides). "
    "I do not provide investment advice, reviews, opinions, or recommendations. "
    "For educational resources, please refer to the Association of Mutual Funds in India (AMFI) Investor Corner: "
    f"{AMFI_EDUCATIONAL_URL}"
)

PERFORMANCE_REJECTION_TEMPLATE = (
    "Compliance Notification: I cannot calculate returns or perform comparative investment evaluations. "
    "For official historical performance and details for '{scheme_name}', please refer directly to the "
    "official factsheet: {factsheet_url}"
)

# Regex Patterns for Personal Identifiable Information (PII)
# Aadhaar card: 12 digits, starting with 2-9, optional spaces
AADHAAR_PATTERN = re.compile(r'\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b')

# PAN Card: 5 letters, 4 digits, 1 letter
PAN_PATTERN = re.compile(r'\b[A-Za-z]{5}\d{4}[A-Za-z]\b')

# Phone: Optional +91 prefix, then 10 digits starting with 6-9 (supports standard formatting)
PHONE_PATTERN = re.compile(r'\b(?:\+?91[\-\s]?)?[6-9]\d{2}[\-\s]?\d{3}[\-\s]?\d{4}\b')

# Email addresses
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Bank accounts: 9 to 18 consecutive digits
ACCOUNT_PATTERN = re.compile(r'\b\d{9,18}\b')

# Target Schemes Mapping (Normalized name to full official name & URL context)
SCHEME_MAPPINGS = {
    "HDFC Mid-Cap Opportunities Fund": {
        "aliases": ["mid-cap", "mid cap", "midcap opportunities", "hdfc mid cap"],
        "factsheet_url": "https://www.hdfcfund.com/products/hdfc-mid-cap-opportunities-fund"
    },
    "HDFC Flexi Cap Fund": {
        "aliases": ["flexi cap", "flexicap", "hdfc flexi", "equity fund"],
        "factsheet_url": "https://www.hdfcfund.com/products/hdfc-flexi-cap-fund"
    },
    "HDFC Focused 30 Fund": {
        "aliases": ["focused 30", "focused30", "focused fund", "hdfc focused"],
        "factsheet_url": "https://www.hdfcfund.com/products/hdfc-focused-30-fund"
    },
    "HDFC ELSS Tax Saver Fund": {
        "aliases": ["elss", "tax saver", "taxsaver", "elss tax", "hdfc elss"],
        "factsheet_url": "https://www.hdfcfund.com/products/hdfc-elss-tax-saver-fund"
    },
    "HDFC Large Cap Fund": {
        "aliases": ["large cap", "largecap", "top 100", "top100", "hdfc large", "hdfc top 100"],
        "factsheet_url": "https://www.hdfcfund.com/products/hdfc-top-100-fund"
    }
}
