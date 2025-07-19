import requests
import uuid
from app.config import GEMINI_API_KEY, TWILIO_SID, TWILIO_AUTH, TWILIO_PHONE
import base64
def generate_id():
    return "POT" + str(uuid.uuid4())[:6].upper()

def save_image_url(file: bytes, filename: str):
    # Always save as .jpg for Gemini compatibility
    if not filename.lower().endswith('.jpg'):
        filename = filename.rsplit('.', 1)[0] + '.jpg'
    path = f"uploads/{filename}"
    with open(path, "wb") as f:
        f.write(file)
    return path, f"http://localhost:8000/uploads/{filename}"  # or upload to cloud later

def detect_pothole_with_gemini(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()

    headers = {
        "x-goog-api-key": GEMINI_API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Is this an image of a road pothole? Reply only yes or no."},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": base64.b64encode(image_data).decode('utf-8')  # workaround for Gemini
                        }
                    }
                ]
            }
        ]
    }

    res = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        headers=headers,
        json=payload
    )

    try:
        response_json = res.json()
        if 'candidates' not in response_json:
            print("Gemini API error:", response_json)
            return False
        return "yes" in response_json['candidates'][0]['content']['parts'][0]['text'].lower()
    except Exception as e:
        print("Error parsing Gemini response:", e)
        print("Raw response:", res.text)
        return False
    return "yes" in res.json()['candidates'][0]['content']['parts'][0]['text'].lower()

def send_whatsapp(to, body):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    payload = {
        "From": TWILIO_PHONE,
        "To": to,
        "Body": body
    }
    response = requests.post(url, data=payload, auth=(TWILIO_SID, TWILIO_AUTH))
    print("Twilio send_whatsapp response:", response.status_code, response.text)
