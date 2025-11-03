from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import qrcode, io

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>Hello World</h1>"

@app.get("/generate-qr/")
def generate_qr(data: str):
    buf = io.BytesIO()
    qrcode.make(data).save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
