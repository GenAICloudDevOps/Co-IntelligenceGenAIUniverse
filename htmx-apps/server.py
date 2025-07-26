from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
import asyncio
import time
from duckduckgo_search import DDGS
from typing import Dict, List, Optional

app = FastAPI(title="HTMX Apps Server")

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
PORT = int(os.getenv("PORT", "8501"))

# In-memory conversation storage (in production, use proper session management)
conversations: Dict[str, List] = {}

# Rate limiting for web search
last_search_time = 0
SEARCH_COOLDOWN = 3  # seconds

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_auth_headers(authorization: Optional[str] = None):
    """Extract and format authorization headers for backend API calls"""
    if authorization and authorization.startswith('Bearer '):
        return {"Authorization": authorization}
    return {}

def make_authenticated_request(method, url, auth_header=None, **kwargs):
    """Make authenticated request to backend API"""
    headers = kwargs.get('headers', {})
    if auth_header:
        headers.update(get_auth_headers(auth_header))
    kwargs['headers'] = headers
    
    if method.upper() == 'POST':
        return requests.post(url, **kwargs)
    elif method.upper() == 'GET':
        return requests.get(url, **kwargs)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    app_type = "ai-chat" if PORT == 8501 else "document-analysis" if PORT == 8502 else "web-search"
    return {
        "status": "healthy",
        "service": "htmx-apps",
        "port": PORT,
        "app_type": app_type
    }

@app.get("/", response_class=HTMLResponse)
async def serve_app():
    """Serve the appropriate HTMX app based on port"""
    if PORT == 8501:
        return FileResponse("ai_chat.html")
    elif PORT == 8502:
        return FileResponse("document_analysis.html")
    elif PORT == 8503:
        return FileResponse("web_search.html")
    else:
        return HTMLResponse("<h1>HTMX App Server</h1><p>Unknown port configuration</p>")

@app.get("/api/v1/config")
async def get_config():
    """Get backend configuration for status checking"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/config", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Backend unavailable")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Backend connection failed: {str(e)}")

@app.post("/chat")
async def chat(
    message: str = Form(...),
    authorization: Optional[str] = Header(None)
):
    """Handle chat requests"""
    try:
        # Get conversation history for this session (simplified)
        session_id = "default"  # In production, use proper session management
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Call backend API with authentication
        response = make_authenticated_request(
            'POST',
            f"{API_BASE_URL}/api/v1/bedrock/chat",
            auth_header=authorization,
            json={
                "message": message,
                "conversation_history": conversations[session_id]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            ai_response = response.json()["response"]
            
            # Update conversation history
            conversations[session_id].append({
                "role": "user",
                "content": [{"text": message}]
            })
            conversations[session_id].append({
                "role": "assistant", 
                "content": [{"text": ai_response}]
            })
            
            # Return HTML for HTMX with beautiful styling
            return HTMLResponse(f"""
                <div class="message user">
                    <div class="message-bubble">{message}</div>
                </div>
                <div class="message assistant">
                    <div class="message-bubble">{ai_response}</div>
                </div>
            """)
        else:
            return HTMLResponse(f"""
                <div class="message assistant">
                    <div class="message-bubble" style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white;">
                        Error: {response.status_code} - {response.text}
                    </div>
                </div>
            """)
    except Exception as e:
        return HTMLResponse(f"""
            <div class="message assistant">
                <div class="message-bubble" style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white;">
                    Error connecting to backend: {str(e)}
                </div>
            </div>
        """)

@app.post("/analyze-text")
async def analyze_text(
    text: str = Form(...), 
    analysis_type: str = Form("summary"),
    authorization: Optional[str] = Header(None)
):
    """Handle text analysis requests"""
    try:
        response = make_authenticated_request(
            'POST',
            f"{API_BASE_URL}/api/v1/bedrock/analyze-text",
            auth_header=authorization,
            json={
                "text": text,
                "analysis_type": analysis_type
            },
            timeout=30
        )
        
        if response.status_code == 200:
            analysis = response.json()["analysis"]
            analysis_titles = {
                "summary": "📋 Summary",
                "key_points": "🎯 Key Points", 
                "questions": "❓ Questions",
                "analysis": "🔍 Detailed Analysis"
            }
            title = analysis_titles.get(analysis_type, "Analysis Result")
            
            return HTMLResponse(f"""
                <div class="analysis-result">
                    <h3>{title}</h3>
                    <div style="white-space: pre-wrap; line-height: 1.6;">{analysis}</div>
                </div>
            """)
        else:
            return HTMLResponse(f"""
                <div class="error-message">
                    ❌ Error: {response.status_code} - {response.text}
                </div>
            """)
    except Exception as e:
        return HTMLResponse(f"""
            <div class="error-message">
                ❌ Error connecting to backend: {str(e)}
            </div>
        """)

@app.post("/analyze-document")
async def analyze_document(
    file: UploadFile = File(...), 
    analysis_type: str = Form("summary"),
    authorization: Optional[str] = Header(None)
):
    """Handle document analysis requests"""
    try:
        # Forward file to backend
        files = {"file": (file.filename, await file.read(), file.content_type)}
        data = {"analysis_type": analysis_type}
        
        response = make_authenticated_request(
            'POST',
            f"{API_BASE_URL}/api/v1/bedrock/analyze-document",
            auth_header=authorization,
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            analysis = response.json()["analysis"]
            analysis_titles = {
                "summary": "📋 Summary",
                "key_points": "🎯 Key Points", 
                "questions": "❓ Questions",
                "analysis": "🔍 Detailed Analysis"
            }
            title = analysis_titles.get(analysis_type, "Analysis Result")
            
            return HTMLResponse(f"""
                <div class="analysis-result">
                    <h3>{title}</h3>
                    <div style="white-space: pre-wrap; line-height: 1.6;">{analysis}</div>
                </div>
            """)
        else:
            return HTMLResponse(f"""
                <div class="error-message">
                    ❌ Error: {response.status_code} - {response.text}
                </div>
            """)
    except Exception as e:
        return HTMLResponse(f"""
            <div class="error-message">
                ❌ Error connecting to backend: {str(e)}
            </div>
        """)

async def search_web_with_retry(query: str, max_results: int = 5, max_retries: int = 3) -> List[Dict]:
    """Perform web search with retry logic and rate limiting"""
    global last_search_time
    
    # Rate limiting
    current_time = time.time()
    time_since_last = current_time - last_search_time
    if time_since_last < SEARCH_COOLDOWN:
        await asyncio.sleep(SEARCH_COOLDOWN - time_since_last)
    
    last_search_time = time.time()
    
    for attempt in range(max_retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return results
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                await asyncio.sleep(wait_time)
            else:
                raise e

async def get_ai_analysis_with_auth(search_results: List[Dict], query: str, authorization: Optional[str] = None) -> str:
    """Get AI analysis of search results with authentication"""
    try:
        # Prepare search results for AI analysis
        results_text = "\n\n".join([
            f"Title: {result.get('title', 'N/A')}\n"
            f"Content: {result.get('body', 'N/A')}\n"
            f"URL: {result.get('href', 'N/A')}"
            for result in search_results
        ])
        
        analysis_prompt = f"""
        Based on the following search results for the query "{query}", provide a comprehensive analysis:

        {results_text}

        Please provide:
        1. A summary of the key findings
        2. Main themes and patterns
        3. Important insights or conclusions
        4. Any notable trends or developments
        """
        
        response = make_authenticated_request(
            'POST',
            f"{API_BASE_URL}/api/v1/bedrock/analyze-text",
            auth_header=authorization,
            json={
                "text": analysis_prompt,
                "analysis_type": "analysis"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["analysis"]
        else:
            return f"AI Analysis unavailable (Status: {response.status_code}). Please ensure you are logged in."
            
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

async def get_ai_analysis(search_results: List[Dict], query: str) -> str:
    """Get AI analysis of search results (legacy function for backward compatibility)"""
    return await get_ai_analysis_with_auth(search_results, query, None)

@app.post("/web-search")
async def web_search_endpoint(
    query: str = Form(...), 
    max_results: int = Form(5),
    authorization: Optional[str] = Header(None)
):
    """Handle web search requests"""
    try:
        # Perform web search with rate limiting
        search_results = await search_web_with_retry(query, max_results)
        
        if not search_results:
            return HTMLResponse("""
                <div class="warning-message">
                    ⚠️ No search results found. Try a different query or wait a moment before trying again.
                </div>
            """)
        
        # Get AI analysis with authentication
        ai_analysis = await get_ai_analysis_with_auth(search_results, query, authorization)
        
        # Build HTML response with beautiful styling
        html_parts = [f'<div class="success-message">✅ Found {len(search_results)} results</div>']
        
        # Search results
        html_parts.append('<h3 style="color: white; margin-bottom: 20px; font-size: 1.5em;">📄 Search Results</h3>')
        
        for i, result in enumerate(search_results, 1):
            html_parts.append(f"""
                <div class="result-card">
                    <h4>{i}. {result['title']}</h4>
                    <p>{result['body']}</p>
                    <a href="{result['href']}" target="_blank">🔗 Read more</a>
                </div>
            """)
        
        # AI Analysis
        if ai_analysis and not ai_analysis.startswith("AI Analysis Error"):
            html_parts.append(f"""
                <div class="ai-analysis">
                    <h3>🤖 AI Analysis</h3>
                    <h4>Summary & Insights</h4>
                    <div style="white-space: pre-wrap; line-height: 1.6;">{ai_analysis}</div>
                </div>
            """)
        else:
            html_parts.append('<div class="warning-message">⚠️ AI analysis unavailable. Check your AWS Bedrock configuration.</div>')
            if ai_analysis:
                html_parts.append(f'<div class="error-message">❌ {ai_analysis}</div>')
        
        return HTMLResponse(''.join(html_parts))
        
    except Exception as e:
        return HTMLResponse(f"""
            <div class="error-message">
                ❌ Search error: {str(e)}
            </div>
        """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
