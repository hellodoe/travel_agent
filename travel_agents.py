from agents import Agent, handoff
from tools import (
    search_flights,
    book_flight,
    search_hotels,
    book_hotel,
    get_activities
)

# ==========================================
# Specialized Agents
# ==========================================

flight_agent = Agent(
    name="Flight Specialist",
    instructions=(
        "You are an expert flight assistant. Help the user search for flights and book them. "
        "Use the search_flights tool first. Once the user selects a flight, use the book_flight tool. "
        "After booking a flight, hand off the user to the Hotel Specialist if they need accommodation, "
        "otherwise return control to the Triage Agent."
    ),
    tools=[search_flights, book_flight],
)

hotel_agent = Agent(
    name="Hotel Specialist",
    instructions=(
        "You are an expert hotel assistant. Help the user search for hotels and make bookings. "
        "Use search_hotels to find matches. Use book_hotel to book a room. "
        "After reserving a hotel, hand off the user to the Itinerary Specialist if they want to plan activities, "
        "otherwise return control to the Triage Agent."
    ),
    tools=[search_hotels, book_hotel],
)

itinerary_agent = Agent(
    name="Itinerary Specialist",
    instructions=(
        "You are a local guide and itinerary planner. Help the user find activities, "
        "restaurants, and custom daily schedules using the get_activities tool. "
        "When finished, return control to the Triage Agent."
    ),
    tools=[get_activities],
)

# ==========================================
# Central Concierge / Router Agent
# ==========================================

triage_agent = Agent(
    name="Triage Concierge",
    instructions=(
        "You are the central concierge for a premium travel agency. "
        "Your job is to greet the user, understand their overall travel goals (destination, dates, budget), "
        "and delegate the user to the appropriate specialist:\n"
        "- Hand off to Flight Specialist for flight searches, flight options, or booking flights.\n"
        "- Hand off to Hotel Specialist for lodging, hotel searches, or booking hotel rooms.\n"
        "- Hand off to Itinerary Specialist for activity recommendations, sights, and planning schedules.\n\n"
        "Be warm and polite. If a user asks a general question, answer it, but route them as soon as they have a specific intent."
    ),
    # Declarative Handoff connections
    handoffs=[flight_agent, hotel_agent, itinerary_agent]
)

# ==========================================
# Cross-Agent Handoff Declarations
# ==========================================

flight_agent.handoffs = [hotel_agent, triage_agent]
hotel_agent.handoffs = [itinerary_agent, triage_agent]
itinerary_agent.handoffs = [triage_agent]
