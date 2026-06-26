import asyncio
import os
import sys
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
            print(f"\n[Agent: {current_agent.name}] {result.final_output}")
            
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
