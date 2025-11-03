from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid
import requests
import base64
import datetime
import smtplib
from email.mime.text import MIMEText

# --------------------- DATABASE SETUP ---------------------
DATABASE_URL = "mysql+mysqlconnector://root:@localhost/payments_db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    student_name = Column(String(100))
    roll_no = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    amount = Column(Float)
    txnid = Column(String(50), unique=True)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --------------------- FASTAPI APP ---------------------
app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# PayPal credentials
PAYPAL_CLIENT_ID = "YOUR_PAYPAL_CLIENT_ID"
PAYPAL_SECRET = "YOUR_PAYPAL_SECRET"
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"      # Gmail account sending the email
SMTP_PASS = "your_app_password"         # App password from Gmail
MERCHANT_EMAIL = "merchant_email@gmail.com"  # Merchant receives notification

# --------------------- EMAIL HELPER ---------------------
def send_email_notification(subject: str, message: str):
    """Send email to merchant when payment updates."""
    try:
        msg = MIMEText(message, "plain")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = MERCHANT_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ Email sent to {MERCHANT_EMAIL}")
    except Exception as e:
        print("❌ Email failed:", e)

# --------------------- CREATE PAYMENT ---------------------
@app.post("/create_payment")
def create_payment(
    student_name: str = Form(...),
    roll_no: str = Form(...),
    amount: float = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
):
    txnid = str(uuid.uuid4())[:20]

    db = SessionLocal()
    payment = Payment(
        student_name=student_name,
        roll_no=roll_no,
        email=email,
        phone=phone,
        amount=amount,
        txnid=txnid,
        status="PENDING"
    )
    db.add(payment)
    db.commit()
    db.close()

    # Get PayPal token
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
    token_res = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
    )
    if token_res.status_code != 200:
        return JSONResponse({"error": "Failed to get access token"}, status_code=400)
    access_token = token_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Payment body
    body = {
        "intent": "CAPTURE",
        "purchase_units": [{"reference_id": txnid, "amount": {"currency_code": "USD", "value": str(amount)}}],
        "application_context": {
            "return_url": f"http://127.0.0.1:8000/success?txnid={txnid}",
            "cancel_url": f"http://127.0.0.1:8000/cancel?txnid={txnid}"
        },
    }

    res = requests.post(f"{PAYPAL_API_BASE}/v2/checkout/orders", headers=headers, json=body)
    order = res.json()
    approve_link = next((link["href"] for link in order.get("links", []) if link["rel"] == "approve"), None)

    return RedirectResponse(url=approve_link, status_code=303)

# --------------------- SUCCESS ---------------------
@app.get("/success")
def payment_success(txnid: str, token: str, PayerID: str):
    db = SessionLocal()

    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
    token_res = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
    )
    access_token = token_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    capture_url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{token}/capture"
    res = requests.post(capture_url, headers=headers)
    data = res.json()

    payment = db.query(Payment).filter(Payment.txnid == txnid).first()
    if payment:
        payment.status = "SUCCESS"
        db.commit()
        send_email_notification(
            subject="✅ Payment Successful",
            message=f"Transaction ID: {txnid}\nAmount: {payment.amount}\nStatus: SUCCESS\nStudent: {payment.student_name}",
        )
    db.close()
    return HTMLResponse(f"<h2>✅ Payment Successful for Transaction ID: {txnid}</h2>")

# --------------------- CANCEL ---------------------
@app.get("/cancel")
def payment_cancel(txnid: str):
    db = SessionLocal()
    payment = db.query(Payment).filter(Payment.txnid == txnid).first()
    if payment:
        payment.status = "CANCELLED"
        db.commit()
        send_email_notification(
            subject="❌ Payment Cancelled",
            message=f"Transaction ID: {txnid}\nAmount: {payment.amount}\nStatus: CANCELLED\nStudent: {payment.student_name}",
        )
    db.close()
    return HTMLResponse(f"<h2>❌ Payment Cancelled for Transaction ID: {txnid}</h2>")
