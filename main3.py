import time
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================
SQLALCHEMY_DATABASE_URL = (
    "postgresql://postgres:chetna2920@localhost:5432/hotel_db"
)

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
# EMAIL CONFIGURATION (SMTP)
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "marinehotel814@gmail.com"        # Replace with your email address
SMTP_PASSWORD = "yvau iehz sfxs uscg"        # Replace with your Gmail App Password

def send_confirmation_email(recipient_email: str, booking_details: dict):
    """Function to compose and send confirmation email."""
    if not recipient_email:
        return

    subject = "Booking Confirmation - Your Hotel Stay is Confirmed!"
    
    body = f"""
    Hello {booking_details.get('customer_name')},

    Thank you for choosing our hotel! Your booking has been successfully confirmed.

    --- Booking Details ---
    Booking ID: {booking_details.get('id')}
    Room Type: {booking_details.get('room_type')}
    Check-In Date: {booking_details.get('check_in')}
    Check-Out Date: {booking_details.get('check_out')}
    Number of Guests: {booking_details.get('guests')}
    Number of Days: {booking_details.get('number_of_days')}
    Total Amount: ${booking_details.get('total_amount'):.2f}

    Special Requests: {booking_details.get('special_request') or 'None'}

    We look forward to hosting you!

    Best regards,
    Hotel Management Team
    """

    message = MIMEMultipart()
    message["From"] = SMTP_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, recipient_email, message.as_string())
        server.quit()
        print(f"[SUCCESS] Email sent to {recipient_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

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
    room_number = Column(String(20), nullable=True)
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
    room_number: Optional[str] = None
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
def create_booking(
    booking: BookingCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    if booking.booking_id:
        existing = db.query(HotelBooking).filter(HotelBooking.booking_id == booking.booking_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate Booking ID: Booking with ID {booking.booking_id} already exists."
            )

    # 1. Save initial record
    db_booking = HotelBooking(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # 2. Auto-assign booking_id in pgAdmin if user didn't pass one manually
    if db_booking.booking_id is None:
        db_booking.booking_id = 1000 + db_booking.id  # e.g., Creates Booking IDs like 1001, 1002, 1003...
        db.commit()
        db.refresh(db_booking)

    # 3. Prepare details for confirmation email
    booking_dict = {
        "booking_id": db_booking.booking_id,
        "customer_name": db_booking.customer_name,
        "room_number": db_booking.room_number or "Assigned at Check-in",
        "room_type": db_booking.room_type,
        "check_in": db_booking.check_in,
        "check_out": db_booking.check_out,
        "guests": db_booking.guests,
        "number_of_days": db_booking.number_of_days,
        "total_amount": db_booking.total_amount,
        "special_request": db_booking.special_request,
    }

    # 4. Trigger background email
    if db_booking.email:
        background_tasks.add_task(send_confirmation_email, db_booking.email, booking_dict)

    return db_booking