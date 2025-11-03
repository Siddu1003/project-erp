from fastapi import FastAPI 
from fastapi.responses import StreamingResponse
from fastapi.responses import HTMLResponse
import qrcode
import io

app = FastAPI()





@app.get("/generate-qr/")
def generate_qr(data: str):
    
    qr = qrcode.make(data)

    # Save to memory buffer
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    
    #headers = {
        #'Content-Disposition': f'attachment; filename="{data}.png"' }

    # Return image as response
    return StreamingResponse(buf, media_type="image/png") #headers=headers)
