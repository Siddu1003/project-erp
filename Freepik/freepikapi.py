from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import requests
from fastapi.staticfiles import StaticFiles



app = FastAPI(title="Freepik Image Generator")




FREEPIK_API_KEY = "FREEPIK_API_KEY"
FREEPIK_API_URL = "https://api.freepik.com/v1/ai/mystic"


@app.post("/generate_image")
def generate_image(prompt: str = Form(...)):
    """
    Step 1: Create an image generation task on Freepik
    """
    payload = {
        "prompt": prompt,
        "webhook_url": "https://example.com/webhook",  # dummy, required field
        "resolution": "2k",
        "aspect_ratio": "square_1_1",
        "model": "realism",
        "engine": "automatic",
        "filter_nsfw": True
    }

    headers = {
        "x-freepik-api-key": FREEPIK_API_KEY,
        "Content-Type": "application/json"
    }

    res = requests.post(FREEPIK_API_URL, json=payload, headers=headers)

    if res.status_code != 200:
        return JSONResponse(
            {"error": "Failed to generate image", "details": res.text},
            status_code=res.status_code
        )

    return res.json()  # Returns task_id


@app.get("/check_status/{task_id}")
def check_status(task_id: str):
    """
    Fetch the image generation task status from Freepik.
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
            status_code=res.status_code
        )

    data = res.json()

    # If the generation is done, return image URLs
    generated = data.get("data", {}).get("generated", [])
    if generated:
        urls = [item.get("url") for item in generated if "url" in item]
        return {"status": "COMPLETED", "image_urls": urls}

    # Otherwise show the current status
    status = data.get("data", {}).get("status", "UNKNOWN")
    return {"status": status, "details": data}
