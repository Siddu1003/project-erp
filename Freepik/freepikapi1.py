from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI(title="Freepik Image Generator")

# ✅ Enable CORS so frontend JS can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount frontend folder
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

FREEPIK_API_KEY = "FREEPIK_API_KEY"
FREEPIK_API_URL = "https://api.freepik.com/v1/ai/mystic"


@app.post("/generate_image")
async def generate_image(request: Request):
    """
    Step 1: Create an image generation task on Freepik
    """
    form = await request.form()
    prompt = form.get("prompt")

    if not prompt:
        return JSONResponse({"error": "Prompt is required"}, status_code=422)

    print(f"🎨 Received prompt: {prompt}")

    payload = {
        "prompt": prompt,
        "webhook_url": "https://example.com/webhook",
        "resolution": "2k",
        "aspect_ratio": "square_1_1",
        "model": "realism",
        "engine": "automatic",
        "filter_nsfw": True,
    }

    headers = {
        "x-freepik-api-key": FREEPIK_API_KEY,
        "Content-Type": "application/json",
    }

    res = requests.post(FREEPIK_API_URL, json=payload, headers=headers)
    print(f"🛰️ Freepik POST Status: {res.status_code}")
    print(f"🧾 Freepik Response: {res.text}")

    if res.status_code != 200:
        return JSONResponse(
            {"error": "Failed to generate image", "details": res.text},
            status_code=res.status_code,
        )

    return res.json()


@app.get("/check_status/{task_id}")
def check_status(task_id: str):
    """
    Step 2: Fetch image generation status
    """
    url = f"{FREEPIK_API_URL}/{task_id}"
    headers = {"x-freepik-api-key": FREEPIK_API_KEY}

    res = requests.get(url, headers=headers)
    print("\n--- RAW RESPONSE ---")
    print("Status:", res.status_code)
    print("Text:", res.text)

    if res.status_code != 200:
        return JSONResponse(
            {"error": "Failed to fetch task status", "details": res.text},
            status_code=res.status_code,
        )

    data = res.json()
    generated = data.get("data", {}).get("generated", [])
    if generated:
        urls = [item.get("url") for item in generated if "url" in item]
        return {"status": "COMPLETED", "image_urls": urls}

    status = data.get("data", {}).get("status", "UNKNOWN")
    return {"status": status, "details": data}


@app.get("/", response_class=HTMLResponse)
def root():
    with open(os.path.join("frontend", "index.html"), "r", encoding="utf-8") as f:
        return f.read()
