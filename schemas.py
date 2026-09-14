from pydantic import BaseModel, Field

# Base Schema for shared properties
class BookingBase(BaseModel):
    customer_name: str
    room_type: str
    number_of_days: int = Field(..., gt=0, description="Number of days must be greater than 0")

# Task 4: Pydantic Model for Create Booking
class BookingCreate(BookingBase):
    booking_id: int

# Schema for Updating Booking (Task 8)
class BookingUpdate(BaseModel):
    room_type: str
    number_of_days: int = Field(..., gt=0)

# Task 5: Response Model
class BookingResponse(BookingBase):
    booking_id: int

    class Config:
        from_attributes = True