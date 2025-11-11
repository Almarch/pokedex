from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import httpx
import logging
import json
import os
from datetime import datetime
import uuid
from typing import Dict, Any, Optional, Union
from .Agent import Agent
import yaml
from .config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/logs/agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ollama-agent")

# Initialize FastAPI application
app = FastAPI(title="Ollama Agent Proxy")

# Initialize HTTP client with infinite timeout for streaming responses
http_client = httpx.AsyncClient(timeout=None)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

def generate_request_id() -> str:
    """Generate a unique ID for tracking requests."""
    return f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"

async def log_transaction(
    request_id: str, 
    direction: str, 
    method: str, 
    path: str, 
    headers: Dict[str, str], 
    body: Optional[Union[Dict[str, Any], str, bytes]] = None,
    status_code: Optional[int] = None
) -> None:
    """
    Log transaction details to a JSON file.
    
    Args:
        request_id: Unique identifier for the request
        direction: 'request' or 'response'
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        headers: HTTP headers
        body: Request or response body
        status_code: HTTP status code (for responses only)
    """
    timestamp = datetime.now().isoformat()
    
    # Create log entry base
    log_entry = {
        "request_id": request_id,
        "timestamp": timestamp,
        "direction": direction,
        "method": method,
        "path": path,
        "headers": {k: v for k, v in headers.items() if k.lower() not in ["authorization"]}
    }
    
    # Add status code for responses
    if status_code is not None:
        log_entry["status_code"] = status_code
    
    # Process and add body if present
    if body is not None:
        if isinstance(body, (dict, list)):
            log_entry["body"] = body
        elif isinstance(body, bytes):
            try:
                decoded_body = body.decode("utf-8")
                try:
                    log_entry["body"] = json.loads(decoded_body)
                except json.JSONDecodeError:
                    log_entry["body"] = decoded_body if len(decoded_body) < 10000 else f"{decoded_body[:9000]}... [truncated]"
            except UnicodeDecodeError:
                log_entry["body"] = "[binary data]"
        elif isinstance(body, str):
            try:
                log_entry["body"] = json.loads(body)
            except json.JSONDecodeError:
                log_entry["body"] = body if len(body) < 10000 else f"{body[:9000]}... [truncated]"
    
    # Create filename based on request_id and direction
    filename = f"{request_id}_{direction}.json"
    filepath = os.path.join(config["logs"]["path"], filename)
    
    # Write log to file
    with open(filepath, "w") as f:
        json.dump(log_entry, f, indent=2)
    
    # Log basic info to console
    log_message = f"{direction.upper()} {request_id}: {method} {path}"
    if status_code:
        log_message += f" (Status: {status_code})"
    logger.info(log_message)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def proxy_endpoint(request: Request, path: str):
    """
    Generic endpoint to proxy all requests to Ollama service.
    Logs both the request and response data.
    """
    request_id = generate_request_id()
    method = request.method
    url = config["ollama"]["url"]
    
    # Get request headers and body
    headers = dict(request.headers)
    body = await request.body()

    # Determine if this is a streaming endpoint
    is_streaming = False
    if path.startswith("api/"):
        endpoint = path.split("/")[-1]
        if endpoint in ["generate", "chat"]:
            body_str = body.decode("utf-8")
            body_dict = json.loads(body_str)
            is_streaming = body_dict.get("stream", False)
    
    try:
        if is_streaming:

            # Log the incoming request
            await log_transaction(
                request_id=request_id,
                direction="request_raw",
                method=method,
                path=path,
                headers=headers,
                body=body
            )

            agent = MyAgent(body_dict)
            new_body_dict = agent.process()
            new_body_str = json.dumps(new_body_dict)
            new_body = new_body_str.encode("utf-8")

            headers = {
                "content-type": "application/json",
                "accept": "*/*"
            }

            # Log the processed request
            await log_transaction(
                request_id=request_id,
                direction="request_processed",
                method=method,
                path=path,
                headers=headers,
                body=new_body
            )

            # Utilisation de http_client.stream pour traiter la réponse en streaming
            async def stream_response():
                collected_chunks = []
                
                async with http_client.stream(
                    method=method,
                    url=url,
                    headers=headers,
                    content=new_body,
                    params=request.query_params
                ) as ollama_response:
                    # Capture response status and headers for logging
                    response_status = ollama_response.status_code
                    response_headers = dict(ollama_response.headers)
                    
                    async for chunk in ollama_response.aiter_bytes():
                        collected_chunks.append(chunk)
                        yield chunk
                
                # Stream completed - log the complete response
                complete_response = b''.join(collected_chunks)
                complete_text = complete_response.decode('utf-8', errors='replace')
                
                # Log the complete response as raw text
                await log_transaction(
                    request_id=request_id,
                    direction="response_complete",
                    method=method,
                    path=path,
                    headers=response_headers,
                    body={"raw_text": complete_text[:10000] if len(complete_text) > 10000 else complete_text},
                    status_code=response_status
                )

            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        
        else:
            '''
            Handle regular (non-streaming) response'
            This includes :
            - Calls not to api/chat or api/generate
            - Chat tasks like:
                - Generate a concise, 3-5 word title with an emoji summarizing the chat history.
                - You are an autocompletion system.
            '''

            ollama_response = await http_client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # Return the response to the client
            return Response(
                content=ollama_response.content,
                status_code=ollama_response.status_code,
                headers=dict(ollama_response.headers)
            )
    
    except Exception as e:
        # Log any errors that occur
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        await log_transaction(
            request_id=request_id,
            direction="error",
            method=method,
            path=path,
            headers={},
            body=error_details,
            status_code=500
        )
        
        logger.info(f"Error processing request {request_id}: {str(e)}")
        
        # Return error response
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )