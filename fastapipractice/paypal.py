import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

app = FastAPI(title="PayPal Payment Gateway", version="1.0")

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_BASE_URL = os.getenv("PAYPAL_BASE_URL")

# In-memory store
payments_db: Dict[str, dict] = {}

# -------------------- MODELS --------------------
class CreatePaymentRequest(BaseModel):
    amount: str
    currency: str = "INR"
    description: str

# -------------------- HELPERS --------------------
async def get_paypal_access_token():
    async with httpx.AsyncClient() as client:
        auth = (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "client_credentials"}
        response = await client.post(f"{PAYPAL_BASE_URL}/v1/oauth2/token", auth=auth, data=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get PayPal access token")
        return response.json()["access_token"]

# -------------------- ENDPOINTS --------------------
@app.post("/payments/create")
async def create_payment(req: CreatePaymentRequest):
    access_token = await get_paypal_access_token()

    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": req.currency,
                        "value": req.amount
                    },
                    "description": req.description
                }
            ],
            "application_context": {
                "return_url": "http://localhost:8000/payments/success",
                "cancel_url": "http://localhost:8000/payments/failed"
            }
        }
        response = await client.post(f"{PAYPAL_BASE_URL}/v2/checkout/orders", headers=headers, json=data)

    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    order = response.json()
    payment_id = order["id"]
    payments_db[payment_id] = {"status": "pending", "details": order}

    return {
        "payment_id": payment_id,
        "status": "pending",
        "approve_link": next(link["href"] for link in order["links"] if link["rel"] == "approve")
    }

@app.post("/payments/capture")
async def capture_payment(payment_id: str = Query(..., description="PayPal order ID to capture")):
    access_token = await get_paypal_access_token()

    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}
        response = await client.post(f"{PAYPAL_BASE_URL}/v2/checkout/orders/{payment_id}/capture", headers=headers)

    if response.status_code != 201:
        payments_db[payment_id]["status"] = "failed"
        raise HTTPException(status_code=response.status_code, detail="Payment capture failed")

    capture_data = response.json()
    payments_db[payment_id]["status"] = "successful"
    payments_db[payment_id]["details"] = capture_data

    return {"payment_id": payment_id, "status": "successful", "details": capture_data}

@app.get("/payments/{payment_id}")
async def get_payment_status(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.get("/payments/all")
async def list_all_payments():
    return {"total": len(payments_db), "payments": payments_db}


@app.get("/payments/success")
async def payment_success(order_id: str):
    payments_db[order_id]["status"] = "successful"
    return {"message": "Payment successful", "order_id": order_id}

@app.get("/payments/failed")
async def payment_failed(order_id: str):
    payments_db[order_id]["status"] = "failed"
    return {"message": "Payment failed", "order_id": order_id}
