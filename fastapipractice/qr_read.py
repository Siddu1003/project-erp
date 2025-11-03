from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import requests

app = FastAPI()


API_KEY = "6a4a7928caef9c174646818b5bbde536"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

@app.get("/weather/{city}")
def get_weather(city: str):
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  
    }
    response = requests.get(BASE_URL, params=params)

 
    data = response.json()

   
    if response.status_code != 200:
        return {"error": data.get("message", "Failed to fetch weather")}

   
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "weather": data["weather"][0]["description"]
    }

@app.post("/read-qr/")
async def read_qr(file: UploadFile = File(...)):
    # Read file bytes
    file_bytes = await file.read()
    np_arr = np.frombuffer(file_bytes, np.uint8)
    
    # Decode image with OpenCV
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)

    if not data:
        return JSONResponse(content={"error": "No QR code found"}, status_code=400)

    return {"data": data}
