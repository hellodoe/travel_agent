import os
import httpx
from typing import List, Dict, Any, Optional
from models import FlightBookingRequest, HotelBookingRequest
# pyrefly: ignore [missing-import]
from agents import function_tool

# ==========================================
# Mock Database Definitions
# ==========================================


HOTEL_DB = {
    "PAR": [
        {"hotel_id": "HT-Grand-Paris", "name": "Grand Palace Hotel Paris", "price_per_night": 180.00, "rating": 4.8, "url": "https://www.booking.com/hotel/fr/le-grand-paris.html"},
        {"hotel_id": "HT-Cozy-Paris", "name": "Cozy Stay Inn Paris", "price_per_night": 95.00, "rating": 4.2, "url": "https://www.booking.com/hotel/fr/cozy-stay-paris.html"},
    ],
    "LON": [
        {"hotel_id": "HT-Royal-London", "name": "Royal Savoy London", "price_per_night": 220.00, "rating": 4.9, "url": "https://www.booking.com/hotel/gb/the-savoy.html"},
        {"hotel_id": "HT-Metro-London", "name": "Metro Central Lodge", "price_per_night": 110.00, "rating": 4.0, "url": "https://www.booking.com/hotel/gb/metro-lodge.html"},
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

async def _resolve_place_id(query: str, headers: dict, host: str) -> str:
    url = f"https://{host}/web/flights/auto-complete"
    params = {"query": query, "locale": "en-US"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=15.0)
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data:
                    return data[0].get("PlaceId", query.upper())
    except Exception as e:
        print(f"[Warning] Failed to resolve place ID for '{query}': {e}")
    return query.upper()

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
    
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "sky-scrapper.p.rapidapi.com")
    
    if not RAPIDAPI_KEY or "your-rapidapi-key" in RAPIDAPI_KEY:
        raise ValueError("RapidAPI key not configured in .env file. Please check your setup.")

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    if "flights-sky" in RAPIDAPI_HOST:
        resolved_origin = await _resolve_place_id(origin, headers, RAPIDAPI_HOST)
        resolved_destination = await _resolve_place_id(destination, headers, RAPIDAPI_HOST)
        
        url = f"https://{RAPIDAPI_HOST}/web/flights/search-one-way"
        params = {
            "placeIdFrom": resolved_origin,
            "placeIdTo": resolved_destination,
            "departDate": departure_date,
            "cabinClass": "economy",
            "adults": "1",
            "currency": "USD",
            "market": "US",
            "locale": "en-US"
        }
    else:
        url = f"https://{RAPIDAPI_HOST}/api/v1/flights/searchFlights"
        params = {
            "originSkyId": origin.upper(),
            "destinationSkyId": destination.upper(),
            "date": departure_date,
            "cabinClass": "economy",
            "adults": "1"
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=45.0)
        
        if response.status_code != 200:
            print(f" -> API Error Response ({response.status_code}): {response.text}")
            response.raise_for_status()
            
        data = response.json()
        
        if not data.get("status", True):
            error_msg = data.get("message", "Unknown error")
            errors = data.get("errors")
            if errors:
                error_msg += f" ({errors})"
            raise ValueError(f"RapidAPI Search Error: {error_msg}")
            
        itineraries = data.get("data", {}).get("itineraries", []) if data.get("data") else []
        
        if isinstance(itineraries, dict):
            flights_data = []
            seen_ids = set()
            buckets = itineraries.get("buckets", [])
            for bucket in buckets:
                for item in bucket.get("items", []):
                    item_id = item.get("id")
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        flights_data.append(item)
            if not flights_data:
                flights_data = itineraries.get("results", [])
        else:
            flights_data = itineraries

        results = []
        for item in flights_data[:5]:
            legs = item.get("legs", [{}])[0]
            carriers = legs.get("carriers", {}).get("marketing", [{}])[0]
            
            results.append({
                "flight_id": item.get("id", "N/A"),
                "airline": carriers.get("name", "Unknown Airline"),
                "price": float(item.get("price", {}).get("raw", 0.0)),
                "time": legs.get("departure", "N/A"),
                "origin": origin,
                "destination": destination
            })
            
        if not results:
            raise ValueError("No flights returned from the search API.")
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
    
    return {
        "status": "success",
        "booking_reference": "FL-XYZ987",
        "flight_id": booking.flight_id,
        "airline": "Selected Carrier",
        "price": 490.00,
        "seat": booking.seat_preference,
        "message": "Flight booked successfully!"
    }

async def _resolve_dest_id(query: str, headers: dict, host: str) -> tuple:
    url = f"https://{host}/v1/hotels/locations"
    params = {"name": query, "locale": "en-gb"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=15.0)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list):
                    return data[0].get("dest_id"), data[0].get("dest_type")
    except Exception as e:
        print(f"[Warning] Failed to resolve destination ID for '{query}': {e}")
    raise ValueError(f"Could not resolve destination ID for '{query}'")

def _get_mock_hotels(location: str) -> List[Dict[str, Any]]:
    loc_key = location.upper()
    results = HOTEL_DB.get(loc_key, [])
    if not results:
        for key, val in HOTEL_DB.items():
            if key in loc_key or loc_key in key:
                results = val
                break
    if not results:
        # Dynamically generate mock hotels for any city not in the hardcoded HOTEL_DB
        loc_display = location.strip().title()
        results = [
            {
                "hotel_id": f"HT-{loc_key}-Grand",
                "name": f"Grand Plaza Hotel {loc_display}",
                "price_per_night": 140.00,
                "rating": 4.7,
                "location": loc_key,
                "url": f"https://www.booking.com/searchresults.html?ss={loc_display.replace(' ', '+')}+Grand+Plaza"
            },
            {
                "hotel_id": f"HT-{loc_key}-Cozy",
                "name": f"Cozy Boutique Retreat {loc_display}",
                "price_per_night": 85.00,
                "rating": 4.1,
                "location": loc_key,
                "url": f"https://www.booking.com/searchresults.html?ss={loc_display.replace(' ', '+')}+Cozy+Boutique"
            }
        ]
    return results

@function_tool
async def search_hotels(location: str, checkin: str, checkout: Optional[str] = None, guests: int = 1) -> List[Dict[str, Any]]:
    """
    Search for hotels at the destination location.
    Args:
        location: City code or name (e.g. PAR, LON)
        checkin: Check-in date in YYYY-MM-DD format
        checkout: Check-out date in YYYY-MM-DD format (optional)
        guests: Number of guests
    """
    if not checkout:
        from datetime import datetime, timedelta
        try:
            checkin_dt = datetime.strptime(checkin, "%Y-%m-%d")
            checkout_dt = checkin_dt + timedelta(days=1)
            checkout = checkout_dt.strftime("%Y-%m-%d")
        except Exception:
            checkout = checkin

    print(f"\n[Tool Execution: search_hotels]")
    print(f" -> Location: {location}, Checkin: {checkin}, Checkout: {checkout}, Guests: {guests}")
    
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    HOTEL_RAPIDAPI_HOST = os.getenv("HOTEL_RAPIDAPI_HOST", "booking-com.p.rapidapi.com")
    
    if not RAPIDAPI_KEY or "your-rapidapi-key" in RAPIDAPI_KEY:
        print("[RapidAPI] Key not configured. Using local mock database.")
        return _get_mock_hotels(location)

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": HOTEL_RAPIDAPI_HOST
    }

    try:
        dest_id, dest_type = await _resolve_dest_id(location, headers, HOTEL_RAPIDAPI_HOST)
        
        url = f"https://{HOTEL_RAPIDAPI_HOST}/v1/hotels/search"
        params = {
            "dest_id": dest_id,
            "dest_type": dest_type,
            "checkin_date": checkin,
            "checkout_date": checkout,
            "adults_number": str(guests),
            "room_number": "1",
            "units": "metric",
            "locale": "en-gb",
            "filter_by_currency": "USD"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=20.0)
            response.raise_for_status()
            data = response.json()
            
            hotels_data = data.get("result", [])
            results = []
            
            for item in hotels_data[:5]:
                min_price = item.get("min_total_price", 0.0)
                try:
                    price = float(min_price) / max(1, (guests or 1))
                except Exception:
                    price = 150.00
                
                url = item.get("url")
                if not url:
                    hotel_name_encoded = item.get("hotel_name", "Unknown Hotel").replace(" ", "+")
                    url = f"https://www.booking.com/searchresults.html?ss={hotel_name_encoded}"
                
                results.append({
                    "hotel_id": str(item.get("hotel_id", "")),
                    "name": item.get("hotel_name", "Unknown Hotel"),
                    "price_per_night": price,
                    "rating": float(item.get("review_score", 0.0) / 2.0),
                    "location": location,
                    "url": url
                })
            
            if not results:
                raise ValueError("No hotels returned from the search API.")
            return results

    except Exception as e:
        print(f"[RapidAPI Hotel Error] {e}. Falling back to local mock data.")
        return _get_mock_hotels(location)

@function_tool
async def book_hotel(booking: HotelBookingRequest) -> Dict[str, Any]:
    """
    Book a hotel room using a HotelBookingRequest schema.
    Args:
        booking: A structured HotelBookingRequest detailing hotel_id, room_type, and include_breakfast
    """
    print(f"\n[Tool Execution: book_hotel]")
    print(f" -> Hotel ID: {booking.hotel_id}, Room Type: {booking.room_type}, Breakfast: {booking.include_breakfast}")
    
    hotel_name = "Selected Premium Hotel"
    for loc, hotels in HOTEL_DB.items():
        match = next((h for h in hotels if str(h["hotel_id"]) == str(booking.hotel_id)), None)
        if match:
            hotel_name = match["name"]
            break
            
    return {
        "status": "success",
        "booking_reference": "HT-ABC123",
        "hotel_name": hotel_name,
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
