import os

# Project Path Setup
SUBPHASE_DIR = os.path.dirname(os.path.abspath(__file__))
INGESTION_ROOT = os.path.dirname(SUBPHASE_DIR)
WORKSPACE_ROOT = os.path.dirname(INGESTION_ROOT)

# Directories for each subphase
RAW_DIR = os.path.join(INGESTION_ROOT, "subphase_1_2_scraper", "data", "raw")
CLEANED_DIR = os.path.join(INGESTION_ROOT, "subphase_1_3_cleaner", "data", "cleaned")
CHUNKS_DIR = os.path.join(INGESTION_ROOT, "subphase_1_4_chunker", "data", "chunks")
MOCK_DIR = os.path.join(SUBPHASE_DIR, "data", "mock")

# Ensure directories exist
for path in [RAW_DIR, CLEANED_DIR, CHUNKS_DIR, MOCK_DIR]:
    os.makedirs(path, exist_ok=True)

# Configuration Flags
USE_MOCK_FALLBACK = True  # If True, scraper uses local mock data to guarantee execution
SCRAPE_DELAY = 1.0       # Delay in seconds between requests for polite scraping
CHUNK_SIZE = 300         # Target size of semantic chunks (in characters)
CHUNK_OVERLAP = 75       # Overlap between adjacent chunks (in characters)

# AMC Definition
AMC_NAME = "HDFC Mutual Fund"

# Scheme Registry
SCHEMES = [
    {
        "id": "hdfc_mid_cap",
        "name": "HDFC Mid-Cap Opportunities Fund",
        "category": "Mid-Cap",
        "groww_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "official_sources": [
            {
                "url": "https://www.hdfcfund.com/products/hdfc-mid-cap-opportunities-fund",
                "doc_type": "scheme_page",
                "filename": "hdfc_mid_cap.html"
            },
            {
                "url": "https://www.hdfcfund.com/sid/hdfc-mid-cap-opportunities-fund.pdf",
                "doc_type": "SID",
                "filename": "hdfc_mid_cap_sid.html"
            }
        ]
    },
    {
        "id": "hdfc_flexi_cap",
        "name": "HDFC Flexi Cap Fund",
        "category": "Flexi-Cap",
        "groww_url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "official_sources": [
            {
                "url": "https://www.hdfcfund.com/products/hdfc-flexi-cap-fund",
                "doc_type": "scheme_page",
                "filename": "hdfc_flexi_cap.html"
            },
            {
                "url": "https://www.hdfcfund.com/sid/hdfc-flexi-cap-fund.pdf",
                "doc_type": "SID",
                "filename": "hdfc_flexi_cap_sid.html"
            }
        ]
    },
    {
        "id": "hdfc_focused_30",
        "name": "HDFC Focused 30 Fund",
        "category": "Focused",
        "groww_url": "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
        "official_sources": [
            {
                "url": "https://www.hdfcfund.com/products/hdfc-focused-30-fund",
                "doc_type": "scheme_page",
                "filename": "hdfc_focused_30.html"
            }
        ]
    },
    {
        "id": "hdfc_elss_tax_saver",
        "name": "HDFC ELSS Tax Saver Fund",
        "category": "ELSS / Tax Saver",
        "groww_url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        "official_sources": [
            {
                "url": "https://www.hdfcfund.com/products/hdfc-elss-tax-saver-fund",
                "doc_type": "scheme_page",
                "filename": "hdfc_elss_tax_saver.html"
            }
        ]
    },
    {
        "id": "hdfc_large_cap",
        "name": "HDFC Large Cap Fund",
        "category": "Large-Cap",
        "groww_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        "official_sources": [
            {
                "url": "https://www.hdfcfund.com/products/hdfc-top-100-fund",
                "doc_type": "scheme_page",
                "filename": "hdfc_large_cap.html"
            }
        ]
    }
]

# General Guides & FAQs (AMC / AMFI / SEBI)
GENERAL_SOURCES = [
    {
        "id": "hdfc_faq",
        "name": "HDFC Mutual Fund General FAQ & Statement Help",
        "url": "https://www.hdfcfund.com/information/faq",
        "doc_type": "FAQ",
        "filename": "hdfc_faq.html"
    },
    {
        "id": "amfi_guidance",
        "name": "AMFI Investor Corner Guidance",
        "url": "https://www.amfiindia.com/investor-corner/knowledge-center",
        "doc_type": "guide",
        "filename": "amfi_guidance.html"
    }
]
