from pydantic import BaseModel, Field
from typing import Optional

class FlightBookingRequest(BaseModel):
    """Schema for selecting and booking a flight."""
    flight_id: str = Field(..., description="Unique identifier of the selected flight option (e.g. AA-101)")
    seat_preference: str = Field("window", description="Window, Aisle, or Middle seat preference")
    meal_preference: Optional[str] = Field(None, description="Special dietary request (e.g., Vegetarian, Kosher)")

class HotelBookingRequest(BaseModel):
    """Schema for selecting and booking a hotel room."""
    hotel_id: str = Field(..., description="Unique identifier of the selected hotel option (e.g. HT-Grand)")
    room_type: str = Field("standard", description="Standard, Deluxe, or Suite")
    include_breakfast: bool = Field(default=False, description="Whether breakfast should be included in the booking")
