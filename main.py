import asyncio
import os
import sys

# Force UTF-8 encoding for standard output/error to prevent Windows console crashes when printing Unicode ratings (like ★)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from agents import Runner
from travel_agents import triage_agent

# Load environment variables
load_dotenv()

# Verify API key is present
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your-openai-api-key-here":
    print("Warning: OPENAI_API_KEY is not set. Please set it in your .env file.")
    print("Example: OPENAI_API_KEY=sk-proj-...")

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

async def run_interactive_loop():
    print("=" * 60)
    print("          OPENAI AGENTS TRAVEL ASSISTANT CLI           ")
    print("=" * 60)
    print("Ready to plan your trip! Type 'exit' or 'quit' to end.")
    print("-" * 60)
    
    # Initialize history list and set active agent to Triage Concierge
    history = []
    current_agent = triage_agent
    
    # Simple greeting from the triage agent
    print(f"\n[Agent: {current_agent.name}] Hello! I am your travel assistant concierge. How can I help you plan your trip today?")
    
    while True:
        try:
            user_msg = input("\nYou: ").strip()
            if not user_msg:
                continue
            if user_msg.lower() in ["exit", "quit"]:
                print("Goodbye! Safe travels!")
                break
                
            # Append new user message to the conversation history list
            history.append({"role": "user", "content": user_msg})
            
            print(f" -> Thinking (routing with {current_agent.name})...")
            
            # Execute agent runner step
            result = await Runner.run(current_agent, input=history)
            
            # Check if agent changed due to handoff
            if result.last_agent.name != current_agent.name:
                print(f"\n[Handoff] Conversation transferred from {current_agent.name} to {result.last_agent.name}")
                current_agent = result.last_agent
                
            # Display final agent output
            response_text = get_last_assistant_message(result)
            print(f"\n[Agent: {current_agent.name}] {response_text}")
            
            # Update history with the full transcript (which converts intermediate states, tool calls, and results)
            history = result.to_input_list()
            
        except KeyboardInterrupt:
            print("\nGoodbye! Safe travels!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please ensure your OPENAI_API_KEY environment variable is configured correctly.")

if __name__ == "__main__":
    # Ensure event loop runs correctly on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_interactive_loop())
