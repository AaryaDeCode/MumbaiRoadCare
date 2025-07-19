import requests
from app.config import GEMINI_API_KEY

def validate_text_with_gemini(text, field_type):
    # Use Gemini to check for abusive or invalid content
    prompt = f"Is the following {field_type} appropriate and non-abusive for a pothole complaint? Reply only yes or no.\n{text}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    headers = {
        "x-goog-api-key": GEMINI_API_KEY
    }
    res = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        headers=headers,
        json=payload
    )
    try:
        response_json = res.json()
        if 'candidates' not in response_json:
            print("Gemini text validation error:", response_json)
            return False
        return "yes" in response_json['candidates'][0]['content']['parts'][0]['text'].lower()
    except Exception as e:
        print("Error parsing Gemini text validation response:", e)
        print("Raw response:", res.text)
        return False
