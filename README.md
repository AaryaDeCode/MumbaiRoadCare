# Mumbai RoadCare - Pothole Complaint Bot & Dashboard

This project enables citizens to report potholes via WhatsApp and provides BMC staff with a dashboard to track, manage, and resolve complaints by ward.

## Features
- **WhatsApp Bot**: Users send pothole images and details via WhatsApp. The bot guides them step-by-step and validates inputs using Google Gemini.
- **Image & Text Validation**: Gemini API checks if the image is a pothole and validates location, area, and description fields.
- **MySQL Database**: Stores all complaints with phone, image, location, area, description, and status.
- **Streamlit Dashboard**: BMC staff can view complaints by ward, mark them as resolved, and (optionally) notify users.
- **Ward Mapping**: Complaints are grouped by ward using a CSV mapping of major areas and lat/lon.

## File Structure
```
pothole-bot/
├── app/
│   ├── main.py            # FastAPI WhatsApp webhook & bot logic
│   ├── db.py              # MySQL connection & DB functions
│   ├── state.py           # In-memory user session tracking
│   ├── utils.py           # Image handling, Gemini, Twilio helpers
│   ├── utils_text_validation.py # Gemini text validation
│   └── config.py          # Loads environment variables
├── dashboard.py           # Streamlit dashboard for BMC
├── WardCode-MajorAreasCovered-ApproximateCentralLat-Long.csv # Ward mapping
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (secrets)
└── README.md              # Project documentation
```

## Setup Instructions
1. **Clone the repository**
2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Configure `.env`**: Add your Gemini, Twilio, and MySQL credentials. Example:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   TWILIO_SID=your_twilio_sid
   TWILIO_AUTH=your_twilio_auth_token
   TWILIO_PHONE=whatsapp:+14155238886
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASS=your_mysql_password
   DB_NAME=pothole_db
   ```
4. **Create MySQL database**:
   - Create a database named `pothole_db` and a table `complaints` with appropriate columns (see `db.py`).
5. **Run FastAPI server**:
   ```powershell
   uvicorn app.main:app --reload
   ```
6. **Expose webhook (for Twilio)**:
   - Use [ngrok](https://ngrok.com/) to expose your local server:
     ```powershell
     ngrok http 8000
     ```
   - Set the ngrok URL as your Twilio WhatsApp webhook.
7. **Run Streamlit dashboard**:
   ```powershell
   streamlit run dashboard.py
   ```

## Usage
- **Citizens**: Send a pothole image to the WhatsApp bot. Follow prompts for location, area, and description.
- **BMC Staff**: Open the Streamlit dashboard to view, filter, and resolve complaints by ward. Mark complaints as "Done" to notify users.

## Technologies Used
- FastAPI
- Streamlit
- MySQL (mysql-connector-python)
- Twilio WhatsApp API
- Google Gemini API
- Python-dotenv
- Pandas

## Notes
- Twilio sandbox has daily message limits.
- Gemini API key required for validation.
- Ensure the CSV file for ward mapping is present in the `pothole-bot` folder.

## License
MIT
