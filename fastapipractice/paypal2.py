from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid
import requests
import base64
import datetime
import json

# ---------------------- Database Setup ----------------------
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

# ---------------------- FastAPI Setup ----------------------
app = FastAPI()
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ---------------------- PayPal Credentials ----------------------
PAYPAL_CLIENT_ID = "PAYPAL_ID"
PAYPAL_SECRET = "PAYPAL_SECRET_KEY"
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"

# Replace with your own Webhook.site URL
WEBHOOK_URL = "https://webhook.site/144d1f3d-decf-4226-bda4-e3ca11df62fe" 


# ---------------------- Helper Function ----------------------
def send_webhook_notification(event_type: str, payment_data: dict):
    """
    Sends a JSON notification to a webhook receiver (e.g., Webhook.site)
    """
    try:
        payload = {
            "event": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "data": payment_data
        }
        requests.post(WEBHOOK_URL, json=payload)
        print(f"✅ Webhook sent for {event_type}")
    except Exception as e:
        print(f"⚠️ Failed to send webhook: {e}")


# ---------------------- Routes ----------------------

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

    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
    token_res = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"},
    )

    if token_res.status_code != 200:
        return JSONResponse({"error": "Failed to get access token"}, status_code=400)

    access_token = token_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": txnid,
                "amount": {"currency_code": "USD", "value": str(amount)}
            }
        ],
        "application_context": {
            "return_url": f"http://127.0.0.1:8000/success?txnid={txnid}",
            "cancel_url": f"http://127.0.0.1:8000/cancel?txnid={txnid}"
        }
    }

    res = requests.post(f"{PAYPAL_API_BASE}/v2/checkout/orders", headers=headers, json=body)
    order = res.json()
    approve_link = next((link["href"] for link in order.get("links", []) if link["rel"] == "approve"), None)

    return RedirectResponse(url=approve_link, status_code=303)


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
        send_webhook_notification("payment_success", {
            "txnid": txnid,
            "student_name": payment.student_name,
            "email": payment.email,
            "amount": payment.amount,
            "status": "SUCCESS"
        })
    db.close()

    return HTMLResponse(f"<h2>Payment Successful for Transaction ID: {txnid}</h2>")


@app.get("/cancel")
def payment_cancel(txnid: str):
    db = SessionLocal()
    payment = db.query(Payment).filter(Payment.txnid == txnid).first()
    if payment:
        payment.status = "CANCELLED"
        db.commit()
        send_webhook_notification("payment_cancelled", {
            "txnid": txnid,
            "student_name": payment.student_name,
            "amount": payment.amount,
            "status": "CANCELLED"
        })
    db.close()
    return HTMLResponse(f"<h2>Payment Cancelled for Transaction ID: {txnid}</h2>")


@app.post("/webhook/paypal")
async def paypal_webhook(request: Request):
    """
    PayPal will send payment updates (success, failed, refunded, etc.)
    to this endpoint automatically.
    """
    body = await request.json()
    event_type = body.get("event_type")
    resource = body.get("resource", {})

    db = SessionLocal()
    txnid = resource.get("invoice_id") or resource.get("id")

    payment = db.query(Payment).filter(Payment.txnid == txnid).first()
    if payment:
        if event_type == "PAYMENT.CAPTURE.COMPLETED":
            payment.status = "SUCCESS"
        elif event_type == "PAYMENT.CAPTURE.DENIED":
            payment.status = "FAILED"
        elif event_type == "PAYMENT.CAPTURE.PENDING":
            payment.status = "PENDING"
        db.commit()
    db.close()

    # Forward this webhook event to merchant’s listener (e.g. webhook.site)
    send_webhook_notification(event_type, body)

    return JSONResponse({"message": "Webhook received successfully"})


@app.get("/payments")
def get_all_payments():
    db = SessionLocal()
    payments = db.query(Payment).all()
    db.close()
    return JSONResponse([
        {
            "id": p.id,
            "student_name": p.student_name,
            "roll_no": p.roll_no,
            "email": p.email,
            "phone": p.phone,
            "amount": p.amount,
            "txnid": p.txnid,
            "status": p.status,
            "created_at": str(p.created_at)
        } for p in payments
    ])


@app.get("/payments/status/{status}")
def get_payments_by_status(status: str):
    db = SessionLocal()
    valid_statuses = ["SUCCESS", "FAILED", "CANCELLED", "PENDING"]

    if status.upper() not in valid_statuses:
        db.close()
        return JSONResponse({"error": f"Invalid status. Choose from {valid_statuses}"}, status_code=400)

    payments = db.query(Payment).filter(Payment.status == status.upper()).all()
    db.close()

    return JSONResponse([
        {
            "id": p.id,
            "student_name": p.student_name,
            "roll_no": p.roll_no,
            "email": p.email,
            "phone": p.phone,
            "amount": p.amount,
            "txnid": p.txnid,
            "status": p.status,
            "created_at": str(p.created_at)
        } for p in payments
    ])
