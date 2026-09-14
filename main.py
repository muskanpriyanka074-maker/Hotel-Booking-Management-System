import time
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ==========================================
# 1. DATABASE CONFIGURATION (SQLite/PostgreSQL)
# ==========================================
# Format: postgresql://<username>:<password>@localhost:5432/<database_name>
SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:chetna2920@localhost:5432/hotel_db"
)

# ✅ Clean engine creation for PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. SQLALCHEMY MODEL
# ==========================================
class HotelBooking(Base):
    __tablename__ = "hotel_bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, unique=True, index=True, nullable=True)
    customer_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    room_type = Column(String(50), nullable=False)
    guests = Column(Integer, default=1)
    number_of_days = Column(Integer, default=1)
    check_in = Column(String(20), nullable=True)
    check_out = Column(String(20), nullable=True)
    total_amount = Column(Float, nullable=True)
    special_request = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. PYDANTIC SCHEMAS
# ==========================================
class BookingCreate(BaseModel):
    booking_id: Optional[int] = None
    customer_name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    room_type: str
    guests: Optional[int] = 1
    number_of_days: Optional[int] = 1
    check_in: Optional[str] = ""
    check_out: Optional[str] = ""
    total_amount: Optional[float] = 0.0
    special_request: Optional[str] = ""

class BookingResponse(BookingCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# 4. FASTAPI APPLICATION SETUP
# ==========================================
app = FastAPI(
    title="Hotel Booking Management API",
    description="Backend API solution connecting Streamlit UI to Database",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    processing_time = (time.time() - start_time) * 1000
    print(f"[LOG] Method: {request.method} | URL: {request.url.path} | Time Taken: {processing_time:.2f} ms")
    response.headers["X-Process-Time-Ms"] = f"{processing_time:.2f}"
    return response

# ==========================================
# 5. API ENDPOINTS
# ==========================================

@app.post("/bookings/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
@app.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    if booking.booking_id:
        existing = db.query(HotelBooking).filter(HotelBooking.booking_id == booking.booking_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate Booking ID: Booking with ID {booking.booking_id} already exists."
            )

    db_booking = HotelBooking(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings/", response_model=List[BookingResponse], status_code=status.HTTP_200_OK)
@app.get("/bookings", response_model=List[BookingResponse], status_code=status.HTTP_200_OK)
def fetch_all_bookings(db: Session = Depends(get_db)):
    return db.query(HotelBooking).all()

@app.delete("/bookings/{booking_id}", status_code=status.HTTP_200_OK)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(HotelBooking).filter(
        (HotelBooking.booking_id == booking_id) | (HotelBooking.id == booking_id)
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking not found: No record exists for ID {booking_id}."
        )

    db.delete(booking)
    db.commit()
    return {"message": f"Booking ID {booking_id} deleted successfully."}