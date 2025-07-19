from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse
from app.utils import save_image_url, detect_pothole_with_gemini, send_whatsapp, generate_id
from app.db import save_complaint, init_db
from app.state import update_user, get_user, clear_user
from app.utils_text_validation import validate_text_with_gemini

import os

from fastapi.staticfiles import StaticFiles

app = FastAPI()
init_db()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.post("/webhook")
async def receive_msg(request: Request,
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None),
    Latitude: str = Form(None),
    Longitude: str = Form(None)
):
    # Log incoming form data for debugging
    form = await request.form()
    print("Incoming Twilio data:", dict(form))

    phone_number = From
    user_data = get_user(phone_number)

    # Handle image if present
    if MediaUrl0:
        filename = f"{phone_number.replace('+', '')}_pothole.jpg"
        # Download image from MediaUrl0 with Twilio Auth
        import requests
        from app.config import TWILIO_SID, TWILIO_AUTH
        img_response = requests.get(MediaUrl0, auth=(TWILIO_SID, TWILIO_AUTH))
        if img_response.status_code == 200:
            img_data = img_response.content
            local_path, image_url = save_image_url(img_data, filename)
            is_pothole = detect_pothole_with_gemini(local_path)
            if not is_pothole:
                send_whatsapp(phone_number, "❌ This image does not appear to show a pothole. Please try again.")
                return JSONResponse({"message": "Not a pothole."})
            update_user(phone_number, "image_url", image_url)
            send_whatsapp(phone_number, "✅ Pothole detected. Please send the following info:\n1. Location\n2. City/Area\n3. Description")
            return JSONResponse({"message": "Image accepted."})
        else:
            send_whatsapp(phone_number, "❌ Failed to download image from WhatsApp. Please try again.")
            return JSONResponse({"message": "Image download failed."})

    # Step-by-step info collection
    data = get_user(phone_number)
    # Step 1: Ask for location
    if "image_url" in data and "location" not in data:
        if Latitude and Longitude:
            location_value = f"Lat: {Latitude}, Lon: {Longitude}"
            update_user(phone_number, "location", location_value)
            send_whatsapp(phone_number, "🏙️ Please provide the city/area of the pothole.")
            return JSONResponse({"message": "Waiting for area."})
        else:
            send_whatsapp(phone_number, "📍 Please send the location using WhatsApp's location feature (not as text). Tap the paperclip and choose Location.")
            return JSONResponse({"message": "Waiting for valid location."})

    # Step 2: Ask for area
    data = get_user(phone_number)
    if "image_url" in data and "location" in data and "area" not in data:
        if Body:
            area_value = Body.strip()
            if validate_text_with_gemini(area_value, "area"):
                update_user(phone_number, "area", area_value)
                send_whatsapp(phone_number, "📝 Please provide a short description of the pothole.")
                return JSONResponse({"message": "Waiting for description."})
            else:
                send_whatsapp(phone_number, "❌ Invalid or inappropriate area. Please provide a valid city/area.")
                return JSONResponse({"message": "Waiting for valid area."})
        else:
            send_whatsapp(phone_number, "🏙️ Please provide the city/area of the pothole.")
            return JSONResponse({"message": "Waiting for area."})

    # Step 3: Ask for description
    data = get_user(phone_number)
    if "image_url" in data and "location" in data and "area" in data and "description" not in data:
        if Body:
            desc_value = Body.strip()
            if validate_text_with_gemini(desc_value, "description"):
                update_user(phone_number, "description", desc_value)
            else:
                send_whatsapp(phone_number, "❌ Invalid or inappropriate description. Please provide a valid description.")
                return JSONResponse({"message": "Waiting for valid description."})
        else:
            send_whatsapp(phone_number, "📝 Please provide a short description of the pothole.")
            return JSONResponse({"message": "Waiting for description."})

    # Step 4: Save complaint
    data = get_user(phone_number)
    required = ["image_url", "location", "area", "description"]
    if all(key in data for key in required):
        complaint_id = generate_id()
        data["complaint_id"] = complaint_id
        data["phone"] = phone_number
        save_complaint(data)
        send_whatsapp(phone_number, f"🆗 Complaint Registered!\nID: {complaint_id}")
        clear_user(phone_number)
        return JSONResponse({"message": "Complaint saved."})
