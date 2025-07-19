import mysql.connector
from app.config import DB_CONFIG

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            complaint_id VARCHAR(20),
            phone VARCHAR(30),
            image_url TEXT,
            location TEXT,
            area TEXT,
            description TEXT,
            status VARCHAR(20) DEFAULT 'registered',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_complaint(data):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO complaints (complaint_id, phone, image_url, location, area, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data['complaint_id'], data['phone'], data['image_url'],
        data.get('location'), data.get('area'), data.get('description')
    ))
    conn.commit()
    cur.close()
    conn.close()
