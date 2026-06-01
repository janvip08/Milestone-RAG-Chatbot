import os
import sys
import shutil
import logging
import uuid
import gc
import streamlit as st
from tornado.web import Application, StaticFileHandler
from tornado.routing import Rule, PathMatches

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("StreamlitApp")

# Ensure root workspace is in sys.path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_core.src.main import run_rag_pipeline

@st.cache_resource
def setup_tornado_routing():
    """
    Configures an in-memory custom Tornado static file route matching /sources/(.*)
    to point directly to the project's mock data folder.
    This routes files securely without making any filesystem writes.
    """
    try:
        # Find the tornado application instance
        tornado_app = next(o for o in gc.get_referrers(Application) if o.__class__ is Application)
        
        # Local mock directory containing documents
        mock_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingestion", "subphase_1_1_registry", "data", "mock")
        
        # Register the static rule at the front of Tornado's routing table
        rule = Rule(PathMatches(r"/sources/(.*)"), StaticFileHandler, {"path": mock_dir})
        tornado_app.wildcard_router.rules.insert(0, rule)
        logger.info(f"Successfully configured Tornado static route for /sources/ -> {mock_dir}")
    except Exception as e:
        logger.error(f"Failed to configure Tornado static route: {str(e)}", exc_info=True)

# Run Tornado routing on app load
setup_tornado_routing()

@st.cache_resource
def initialize_vector_db():
    """
    Checks if ChromaDB contains document chunks. If empty, runs ingestion and seeding automatically.
    """
    try:
        from vector_db.src.store import VectorStoreManager
        store = VectorStoreManager()
        count = store.collection.count()
        logger.info(f"Startup check: ChromaDB Collection count is {count}")
        
        if count == 0:
            logger.info("ChromaDB Collection is empty. Auto-triggering ingestion and database seeding...")
            
            # Execute Phase 1: Ingestion
            from ingestion.main import main as run_ingestion
            run_ingestion()
            
            # Execute Phase 2: Seeding
            from vector_db.src.main import seed_database
            seed_database()
            
            # Recheck count
            count = store.collection.count()
            logger.info(f"Auto-seeding completed. New ChromaDB Collection count: {count}")
        return count
    except Exception as e:
        logger.error(f"Error during startup vector DB initialization: {str(e)}", exc_info=True)
        return 0

# Initialize/Auto-seed vector DB (cached so it runs once per deployment)
collection_size = initialize_vector_db()

# Page Configuration
st.set_page_config(
    page_title="Grow RAG Chatbot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Groww-style Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #090e17 !important;
        color: #d9e2ff !important;
    }
    
    h1, h2, h3, [data-testid="stHeader"] {
        font-family: 'Outfit', sans-serif;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0b111e !important;
        border-right: 1px solid rgba(133, 148, 140, 0.1) !important;
    }
    
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: rgba(0, 208, 156, 0.1);
        border: 1px solid rgba(0, 208, 156, 0.2);
        color: #00d09c;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 12px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00d09c;
    }
    
    /* New Chat button and other buttons */
    div.stButton > button {
        background-color: transparent !important;
        color: #00d09c !important;
        border: 1px solid rgba(0, 208, 156, 0.3) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        padding: 10px !important;
    }
    div.stButton > button:hover {
        background-color: rgba(0, 208, 156, 0.05) !important;
        border-color: #00d09c !important;
        box-shadow: 0 4px 20px rgba(0, 208, 156, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Previous conversation buttons */
    .history-btn-container button {
        background-color: transparent !important;
        color: #bacac1 !important;
        border: 1px solid transparent !important;
        text-align: left !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        width: 100% !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    .history-btn-container button:hover {
        background-color: #152035 !important;
        color: #ffffff !important;
    }

    /* Citation card styling */
    .citation-card {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(133, 148, 140, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-top: 12px;
    }
    
    .citation-link {
        color: #4cd6fb !important;
        font-weight: 600;
        text-decoration: none;
    }
    
    .citation-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

def start_new_chat():
    """Saves current chat (if not empty) to history and resets state."""
    if st.session_state.messages:
        first_query = st.session_state.messages[0]["content"]
        title = first_query[:35] + "..." if len(first_query) > 35 else first_query
        
        # Avoid duplicate history entries
        exists = any(h["id"] == st.session_state.current_chat_id for h in st.session_state.chat_history)
        if not exists:
            st.session_state.chat_history.append({
                "id": st.session_state.current_chat_id,
                "title": title,
                "messages": list(st.session_state.messages)
            })
        else:
            for h in st.session_state.chat_history:
                if h["id"] == st.session_state.current_chat_id:
                    h["messages"] = list(st.session_state.messages)
                    h["title"] = title
                    break
                    
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.messages = []

def load_chat(chat_id):
    """Saves current chat and loads a selected chat session."""
    if st.session_state.messages:
        first_query = st.session_state.messages[0]["content"]
        title = first_query[:35] + "..." if len(first_query) > 35 else first_query
        for h in st.session_state.chat_history:
            if h["id"] == st.session_state.current_chat_id:
                h["messages"] = list(st.session_state.messages)
                h["title"] = title
                break
        else:
            st.session_state.chat_history.append({
                "id": st.session_state.current_chat_id,
                "title": title,
                "messages": list(st.session_state.messages)
            })
            
    for h in st.session_state.chat_history:
        if h["id"] == chat_id:
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = list(h["messages"])
            break

# Sidebar Layout
with st.sidebar:
    st.markdown('<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">'
                '<span style="font-size: 24px; color: #00d09c;">📈</span>'
                '<h2 style="margin: 0; font-size: 24px; font-weight: 700; color: #ffffff;">Grow RAG</h2>'
                '</div>', unsafe_allow_html=True)
    st.markdown('<span style="font-size: 11px; font-weight: 600; color: #85948c; display: block; margin-bottom: 24px;">'
                'Facts-Only Mutual Fund Q&A</span>', unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("➕ New Chat"):
        start_new_chat()
        st.rerun()
        
    st.markdown("<hr style='margin: 16px 0; border: 0; border-top: 1px solid rgba(133, 148, 140, 0.1);'>", unsafe_allow_html=True)
    
    # Previous Conversations list
    if st.session_state.chat_history:
        st.markdown('<span style="font-size: 11px; font-weight: 700; color: #85948c; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; display: block;">Previous Conversations</span>', unsafe_allow_html=True)
        for chat in reversed(st.session_state.chat_history):
            st.markdown('<div class="history-btn-container">', unsafe_allow_html=True)
            # Use visual helper icons inside button labels
            label = f"💬 {chat['title']}"
            if st.button(label, key=f"hist_{chat['id']}"):
                load_chat(chat["id"])
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<hr style='margin: 16px 0; border: 0; border-top: 1px solid rgba(133, 148, 140, 0.1);'>", unsafe_allow_html=True)

    # Suggested Questions list
    st.markdown('<span style="font-size: 11px; font-weight: 700; color: #85948c; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; display: block;">Suggested Questions</span>', unsafe_allow_html=True)
    suggestions = [
        "What is the exit load of HDFC Focused 30 Fund?",
        "What is the benchmark of HDFC Top 100 Fund?",
        "What is the lock-in period for HDFC ELSS Tax Saver Fund?",
        "How can I download my capital gains statement?"
    ]
    for idx, suggestion in enumerate(suggestions):
        if st.button(f"💡 {suggestion}", key=f"sug_{idx}"):
            st.session_state.pending_query = suggestion
            st.rerun()

# Parse helper for backend synthesized citation responses
def parse_citation(response_text: str):
    source_idx = response_text.find("\n\nSource: ")
    if source_idx == -1:
        return response_text.strip(), None, None

    answer = response_text[:source_idx].strip()
    source_block = response_text[source_idx + 2:]
    
    source_url = None
    for line in source_block.split("\n"):
        if line.startswith("Source:"):
            source_url = line.replace("Source:", "").strip()
            break
            
    last_updated = None
    for line in source_block.split("\n"):
        if line.startswith("Last updated from sources:"):
            last_updated = line.replace("Last updated from sources:", "").strip()
            break
            
    return answer, source_url, last_updated

# Main Layout Page Title
st.markdown('<h1 style="font-size: 28px; font-weight: 700; margin-bottom: 8px;">Grow RAG Chatbot</h1>', unsafe_allow_html=True)

# Status Pill
st.markdown(f'<div class="status-pill">'
            f'<div class="status-dot"></div>'
            f'Index: Healthy ({collection_size} chunks)'
            f'</div>', unsafe_allow_html=True)

# Check for pending query from suggestions
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()

# If no messages, render welcome screen
if not st.session_state.messages:
    st.markdown('<div style="text-align: center; padding: 64px 16px;">'
                '<h2 style="font-size: 32px; font-weight: 700; margin-bottom: 12px;">How can I help you today?</h2>'
                '<p style="font-size: 16px; color: #bacac1; max-w-2xl; margin: 0 auto; line-height: 1.6;">'
                'Ask a factual question about listed HDFC schemes, exit loads, lock-in periods, expense ratios, benchmarks, statement downloads, NAVs, or AUMs.'
                '</p>'
                '</div>', unsafe_allow_html=True)

# Render Chat History
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            answer, source_url, last_updated = parse_citation(msg["content"])
            st.markdown(answer)
            
            # Format custom premium citation block
            if source_url:
                filename = source_url.split("/")[-1]
                st.markdown(f"""
                <div class="citation-card" style="margin-bottom: 8px;">
                    <div style="font-size: 11px; font-weight: bold; color: #bacac1; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Sources</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span style="font-size: 16px;">📄</span>
                        <a class="citation-link" href="/sources/{filename}" target="_blank">{filename}</a>
                    </div>
                    <div style="font-size: 11px; font-style: italic; color: rgba(186, 202, 193, 0.6);">
                        Verified from the locked source corpus. {f"• Last updated: {last_updated}" if last_updated else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif last_updated:
                st.markdown(f"<div style='font-size: 11px; font-style: italic; color: rgba(186, 202, 193, 0.6); margin-top: 6px;'>Last updated from sources: {last_updated}</div>", unsafe_allow_html=True)

# Detect if we need to generate response for a new user message
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    query = st.session_state.messages[-1]["content"]
    with st.chat_message("assistant"):
        with st.spinner("Verifying facts and generating answer..."):
            response = run_rag_pipeline(query)
            
        answer, source_url, last_updated = parse_citation(response)
        st.markdown(answer)
        
        if source_url:
            filename = source_url.split("/")[-1]
            st.markdown(f"""
            <div class="citation-card" style="margin-bottom: 8px;">
                <div style="font-size: 11px; font-weight: bold; color: #bacac1; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Sources</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 16px;">📄</span>
                    <a class="citation-link" href="/sources/{filename}" target="_blank">{filename}</a>
                </div>
                <div style="font-size: 11px; font-style: italic; color: rgba(186, 202, 193, 0.6);">
                    Verified from the locked source corpus. {f"• Last updated: {last_updated}" if last_updated else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif last_updated:
            st.markdown(f"<div style='font-size: 11px; font-style: italic; color: rgba(186, 202, 193, 0.6); margin-top: 6px;'>Last updated from sources: {last_updated}</div>", unsafe_allow_html=True)
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# User Input Box
if prompt := st.chat_input("Ask a factual question about listed HDFC schemes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Persistent Footer Disclaimer
st.markdown("""
<div style="position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; padding: 10px; background-color: #090e17; border-top: 1px solid rgba(133, 148, 140, 0.1); z-index: 100;">
    <span style="font-size: 11px; font-weight: 600; color: rgba(186, 202, 193, 0.5); text-transform: uppercase; letter-spacing: 0.05em;">
        Facts-only. No investment advice.
    </span>
</div>
""", unsafe_allow_html=True)
