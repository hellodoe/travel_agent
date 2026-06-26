import os
import sys
from typing import List, Dict, Any, Optional

# Force UTF-8 encoding for standard output/error to prevent Windows console crashes when printing Unicode ratings (like ★)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Runner
from travel_agents import (
    triage_agent,
    flight_agent,
    hotel_agent,
    itinerary_agent
)

# Load environment variables
load_dotenv()

# Verify API key
if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your-openai-api-key-here":
    print("Warning: OPENAI_API_KEY is not set or is using a placeholder.")

app = FastAPI(title="Travel Agent API")

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    active_agent: str = "Triage Concierge"

def get_agent_by_name(name: str):
    name_lower = name.lower()
    if "flight" in name_lower:
        return flight_agent
    elif "hotel" in name_lower:
        return hotel_agent
    elif "itinerary" in name_lower:
        return itinerary_agent
    return triage_agent

def get_last_assistant_message(result) -> str:
    if result.final_output:
        return result.final_output
        
    try:
        history = result.to_input_list()
        for msg in reversed(history):
            if msg.get("role") == "assistant":
                content = msg.get("content")
                if not content:
                    continue
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "output_text":
                            text_parts.append(block.get("text", ""))
                    text = "".join(text_parts).strip()
                    if text:
                        return text
    except Exception as e:
        print(f"Error extracting fallback response: {e}")
        
    return ""

@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    try:
        # Resolve which agent should receive the turn
        agent = get_agent_by_name(payload.active_agent)
        
        # Build the conversation history
        history = list(payload.history)
        history.append({"role": "user", "content": payload.message})
        
        # Execute the Agent run turn
        result = await Runner.run(agent, input=history)
        
        return {
            "response": get_last_assistant_message(result),
            "history": result.to_input_list(),
            "active_agent": result.last_agent.name
        }
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "key_configured": bool(os.getenv("OPENAI_API_KEY"))}

if __name__ == "__main__":
    import uvicorn
    # Set Windows event loop policy
    if sys.platform == 'win32':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
