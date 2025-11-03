from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import uuid
import requests
import base64
import datetime
import pandas as pd
import os


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


app = FastAPI(title="Paypal")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


PAYPAL_CLIENT_ID = "AdsNSglojrc-BnrWe8nPAjzYmvhHL45pQxcZq7_XZ32CC6xQ9EoDJzd994nUEjlE6P-Or1HBlG8JqcSD"
PAYPAL_SECRET = "EEVmj90rX-H87IHzCiocUnvxRbMPyThbklmEOZv5tQW_xhLo7V4B0JtXzzF3dBoivY1O9r7DOtpKNhYY"
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"


EXCEL_FILE = "payments.xlsx"

def save_payment_to_excel(payment):
    """Save a Payment object to Excel (append if file exists)."""
    record = {
        "TransactionID": payment.txnid,
        "StudentName": payment.student_name,
        "RollNo": payment.roll_no,
        "Email": payment.email,
        "Phone": payment.phone,
        "Amount": payment.amount,
        "Status": payment.status,
        "CreatedAt": payment.created_at.strftime("%Y-%m-%d")
    }

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    else:
        df = pd.DataFrame([record])

    df.to_excel(EXCEL_FILE, index=False)


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
        return JSONResponse({"error": "Failed to get access token", "response": token_res.text}, status_code=400)

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
    try:
        order = res.json()
    except Exception as e:
        return JSONResponse({"error": "Invalid JSON", "details": str(e), "response": res.text}, status_code=400)

    if "links" not in order:
        return JSONResponse({"error": "No links in response", "response": order}, status_code=400)

    approve_link = next((link["href"] for link in order["links"] if link["rel"] == "approve"), None)
    if not approve_link:
        return JSONResponse({"error": "Approval link not found", "response": order}, status_code=400)

    return RedirectResponse(url=approve_link, status_code=303)


@app.get("/success")
def payment_success(txnid: str, token: str, PayerID: str):
    db = SessionLocal()

    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
    token_res = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"},
    )
    access_token = token_res.json().get("access_token")

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    capture_url = f"{PAYPAL_API_BASE}/v2/checkout/orders/{token}/capture"
    res = requests.post(capture_url, headers=headers)

    payment = db.query(Payment).filter(Payment.txnid == txnid).first()
    if payment:
        payment.status = "SUCCESS"
        db.commit()
        save_payment_to_excel(payment)  
    db.close()

    return HTMLResponse(f"<h2> Payment Successful for Transaction ID: {txnid}</h2>")


@app.get("/cancel")
def payment_cancel(txnid: str):
    db = SessionLocal()
    payment = db.query(Payment).filter(Payment.txnid == txnid).first()
    if payment:
        payment.status = "CANCELLED"
        db.commit()
        save_payment_to_excel(payment)  
    db.close()

    return HTMLResponse(f"<h2> Payment Cancelled for Transaction ID: {txnid}</h2>")


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
