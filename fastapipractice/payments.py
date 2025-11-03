from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Simple Payment Gateway Simulation API")


payments_db = {}


class PaymentRequest(BaseModel):
    customer_name: str
    amount: int
    currency: str  


class PaymentResponse(BaseModel):
    payment_id: str
    customer_name: str
    amount: int
    currency: str
    status: str



@app.post("/payments/create", response_model=PaymentResponse, tags=["Payments"])
def create_payment(payment: PaymentRequest):
    payment_id = str(uuid.uuid4()) 

    payments_db[payment_id] = {
        "payment_id": payment_id,
        "customer_name": payment.customer_name,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": "pending",
    }

    return payments_db[payment_id]





@app.post("/payments/{payment_id}/complete", response_model=PaymentResponse, tags=["Payments"])
def complete_payment(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment["status"] = "success"
    return payment



@app.post("/payments/{payment_id}/fail", response_model=PaymentResponse, tags=["Payments"])
def fail_payment(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment["status"] = "failed"
    return payment




@app.get("/payments/", response_model=list[PaymentResponse], tags=["Payments"])
def get_all_payments():
    if not payments_db:
        raise HTTPException(status_code=404, detail="No payments found")
    return list(payments_db.values())



@app.get("/payments/{payment_id}", response_model=PaymentResponse, tags=["Payments"])
def get_payment(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment