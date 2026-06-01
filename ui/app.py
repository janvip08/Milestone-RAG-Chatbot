import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add the workspace root directory to python path for imports to work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_core.src import config
from rag_core.src.main import run_rag_pipeline

app = FastAPI(title="HDFC MF FAQ Assistant API")

# Mount mock files directory to serve source documents locally
mock_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ingestion", "subphase_1_1_registry", "data", "mock")
app.mount("/sources", StaticFiles(directory=mock_data_dir), name="sources")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

class ConfigResponse(BaseModel):
    api_key: str
    is_live: bool

class ConfigUpdateRequest(BaseModel):
    api_key: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html not found")
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = run_rag_pipeline(request.query)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    api_key = config.GROQ_API_KEY
    is_live = bool(api_key and api_key.startswith("gsk_"))
    return ConfigResponse(api_key=api_key, is_live=is_live)

@app.post("/api/config")
async def update_config(request: ConfigUpdateRequest):
    key = request.api_key.strip()
    config.GROQ_API_KEY = key
    os.environ["GROQ_API_KEY"] = key
    return {"status": "success"}
