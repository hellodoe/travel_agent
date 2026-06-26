from typing import List, Dict, Any, Optional
from models import FlightBookingRequest, HotelBookingRequest
# pyrefly: ignore [missing-import]
from agents import function_tool

# ==========================================
# Mock Database Definitions
# ==========================================

FLIGHT_DB = [
    {"flight_id": "AA-101", "airline": "American Airlines", "price": 450.00, "time": "08:00 AM", "origin": "NYC", "destination": "PAR"},
    {"flight_id": "DL-202", "airline": "Delta Air Lines", "price": 480.00, "time": "11:30 AM", "origin": "NYC", "destination": "PAR"},
    {"flight_id": "UA-303", "airline": "United Airlines", "price": 520.00, "time": "06:15 PM", "origin": "NYC", "destination": "LON"},
    {"flight_id": "BA-404", "airline": "British Airways", "price": 610.00, "time": "09:00 PM", "origin": "NYC", "destination": "LON"},
]

HOTEL_DB = {
    "PAR": [
        {"hotel_id": "HT-Grand-Paris", "name": "Grand Palace Hotel Paris", "price_per_night": 180.00, "rating": 4.8},
        {"hotel_id": "HT-Cozy-Paris", "name": "Cozy Stay Inn Paris", "price_per_night": 95.00, "rating": 4.2},
    ],
    "LON": [
        {"hotel_id": "HT-Royal-London", "name": "Royal Savoy London", "price_per_night": 220.00, "rating": 4.9},
        {"hotel_id": "HT-Metro-London", "name": "Metro Central Lodge", "price_per_night": 110.00, "rating": 4.0},
    ]
}

ACTIVITIES_DB = {
    "PAR": [
        "Guided historical walking tour of the Louvre area",
        "Eiffel Tower summit priority access",
        "Seine River evening cruise with dining",
        "Palace of Versailles day tour"
    ],
    "LON": [
        "Tower of London and Crown Jewels exhibition",
        "London Eye panoramic experience",
        "West End theatre ticket reservations",
        "British Museum guided highlights tour"
    ]
}

# ==========================================
# Tool Implementations
# ==========================================

@function_tool
async def search_flights(origin: str, destination: str, departure_date: str) -> List[Dict[str, Any]]:
    """
    Search for available flights based on origin, destination, and departure date.
    Args:
        origin: City or airport code of departure (e.g. NYC)
        destination: City or airport code of destination (e.g. PAR or LON)
        departure_date: Date of departure in YYYY-MM-DD format
    """
    print(f"\n[Tool Execution: search_flights]")
    print(f" -> Origin: {origin}, Destination: {destination}, Date: {departure_date}")
    
    results = [f for f in FLIGHT_DB if f["origin"].upper() == origin.upper() and f["destination"].upper() == destination.upper()]
    return results

@function_tool
async def book_flight(booking: FlightBookingRequest) -> Dict[str, Any]:
    """
    Book a flight using a FlightBookingRequest schema.
    Args:
        booking: A structured FlightBookingRequest detailing flight_id, seat_preference, and meal_preference
    """
    print(f"\n[Tool Execution: book_flight]")
    print(f" -> Flight ID: {booking.flight_id}, Seat: {booking.seat_preference}, Meal: {booking.meal_preference}")
    
    flight = next((f for f in FLIGHT_DB if f["flight_id"] == booking.flight_id), None)
    if not flight:
        return {"status": "error", "message": f"Flight {booking.flight_id} not found."}
        
    return {
        "status": "success",
        "booking_reference": "FL-XYZ987",
        "flight_id": booking.flight_id,
        "airline": flight["airline"],
        "price": flight["price"],
        "seat": booking.seat_preference,
        "message": "Flight booked successfully!"
    }

@function_tool
async def search_hotels(location: str, checkin: str, checkout: str, guests: int) -> List[Dict[str, Any]]:
    """
    Search for hotels at the destination location.
    Args:
        location: City code or name (e.g. PAR, LON)
        checkin: Check-in date in YYYY-MM-DD format
        checkout: Check-out date in YYYY-MM-DD format
        guests: Number of guests
    """
    print(f"\n[Tool Execution: search_hotels]")
    print(f" -> Location: {location}, Checkin: {checkin}, Checkout: {checkout}, Guests: {guests}")
    
    loc_key = location.upper()
    results = HOTEL_DB.get(loc_key, [])
    if not results:
        for key, val in HOTEL_DB.items():
            if key in loc_key or loc_key in key:
                results = val
                break
    return results

@function_tool
async def book_hotel(booking: HotelBookingRequest) -> Dict[str, Any]:
    """
    Book a hotel room using a HotelBookingRequest schema.
    Args:
        booking: A structured HotelBookingRequest detailing hotel_id, room_type, and include_breakfast
    """
    print(f"\n[Tool Execution: book_hotel]")
    print(f" -> Hotel ID: {booking.hotel_id}, Room Type: {booking.room_type}, Breakfast: {booking.include_breakfast}")
    
    hotel = None
    for loc, hotels in HOTEL_DB.items():
        hotel = next((h for h in hotels if h["hotel_id"] == booking.hotel_id), None)
        if hotel:
            break
            
    if not hotel:
        return {"status": "error", "message": f"Hotel {booking.hotel_id} not found."}
        
    return {
        "status": "success",
        "booking_reference": "HT-ABC123",
        "hotel_name": hotel["name"],
        "hotel_id": booking.hotel_id,
        "room_type": booking.room_type,
        "message": "Hotel room reserved successfully!"
    }

@function_tool
async def get_activities(city: str, interests: Optional[List[str]] = None) -> List[str]:
    """
    Get recommended activities in a city tailored to user interests.
    Args:
        city: City name or code (e.g. PAR, LON)
        interests: Optional list of categories/interests (e.g., museums, dining, active)
    """
    print(f"\n[Tool Execution: get_activities]")
    print(f" -> City: {city}, Interests: {interests}")
    
    city_key = city.upper()[:3]
    activities = ACTIVITIES_DB.get(city_key, [])
    if not activities:
        for key, val in ACTIVITIES_DB.items():
            if key in city_key or city_key in key:
                activities = val
                break
                
    if not activities:
        activities = [
            f"Walk around the downtown area of {city}",
            f"Try local street food",
            f"Check out the top local tourist spots"
        ]
        
    return activities
