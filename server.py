import os
import sys
from typing import List, Dict, Any, Optional
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
            "response": result.final_output,
            "history": result.to_input_list(),
            "active_agent": result.agent.name
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
