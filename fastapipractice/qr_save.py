from fastapi import FastAPI
import qrcode
import os

app = FastAPI()

# Directory where QR codes will be saved
SAVE_DIR = "generated_qrcodes"
os.makedirs(SAVE_DIR, exist_ok=True)

@app.post("/generate-qr/")
async def generate_qr(data: str):
    # Create QR code
    qr = qrcode.make(data)

    # Define filename
    file_name = f"qr_{hash(data)}.png"
    file_path = os.path.join(SAVE_DIR, file_name)

    # Save QR code image
    qr.save(file_path)

    return {
        "message": "QR code generated successfully!",
        "saved_as": file_path
    }
