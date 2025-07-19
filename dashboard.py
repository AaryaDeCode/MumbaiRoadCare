import streamlit as st
import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# Load ward mapping CSV
ward_df = pd.read_csv(r"C:\Users\aarya\OneDrive\Documents\Projects\MumbaiRoadCare\pothole-bot\WardCode-MajorAreasCovered-ApproximateCentralLat-Long.csv")

# Helper to parse lat/lon from complaint location
import re
def parse_lat_lon(location):
    match = re.search(r"Lat:\s*([\d.]+),\s*Lon:\s*([\d.]+)", location)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

# Connect to MySQL and fetch complaints
def get_complaints():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM complaints")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Assign ward by nearest lat/lon (simple distance)
def assign_ward(lat, lon):
    min_dist = float('inf')
    ward_code = None
    for _, row in ward_df.iterrows():
        coord = row["Approximate Central Lat-Long"]
        if "," in coord and "°" in coord:
            lat_str, lon_str = coord.split(",")
            try:
                ward_lat = float(lat_str.replace("°N", "").strip())
                ward_lon = float(lon_str.replace("°E", "").strip())
                dist = ((lat - ward_lat)**2 + (lon - ward_lon)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    ward_code = row["Ward Code"]
            except:
                continue
    return ward_code

# Dashboard UI
st.title("Mumbai RoadCare - BMC Pothole Complaints Dashboard")
complaints = get_complaints()

# Map complaints to wards
data = []
for c in complaints:
    lat, lon = parse_lat_lon(c.get("location", ""))
    ward = assign_ward(lat, lon) if lat and lon else None
    data.append({**c, "ward": ward})
df = pd.DataFrame(data)

# Show summary by ward
ward_counts = df["ward"].value_counts().reset_index()
ward_counts.columns = ["Ward", "Complaints"]
st.subheader("Complaints by Ward")
st.dataframe(ward_counts)

# Show all complaints, allow status update
st.subheader("All Complaints")
for idx, row in df.iterrows():
    st.markdown(f"**ID:** {row['complaint_id']} | **Ward:** {row['ward']} | **Area:** {row['area']} | **Desc:** {row['description']} | **Status:** {row.get('status', 'Pending')}")
    if st.button(f"Mark as Done (ID: {row['complaint_id']})"):
        # Update status in DB
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE complaints SET status='Done' WHERE complaint_id=%s", (row['complaint_id'],))
        conn.commit()
        conn.close()
        st.success(f"Complaint {row['complaint_id']} marked as Done.")
        # TODO: Send WhatsApp notification to user
        # send_whatsapp(row['phone'], f"✅ Your complaint (ID: {row['complaint_id']}) is resolved!")
        st.experimental_rerun()
