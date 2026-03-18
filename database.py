import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_file='business.db'):
        self.db_file = db_file
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    full_name TEXT,
                    phone TEXT,
                    service_id INTEGER,
                    service_name TEXT,
                    booking_date TEXT,
                    booking_time TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    rating INTEGER,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def create_booking(self, user_id, username, full_name, phone, service_id, service_name, booking_date, booking_time):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookings (user_id, username, full_name, phone, service_id, service_name, booking_date, booking_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, full_name, phone, service_id, service_name, booking_date, booking_time))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_bookings(self, user_id, status='active'):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings
                WHERE user_id = ? AND status = ?
                ORDER BY booking_date, booking_time
            ''', (user_id, status))
            return cursor.fetchall()
    
    def cancel_booking(self, booking_id, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bookings SET status = 'cancelled'
                WHERE id = ? AND user_id = ?
            ''', (booking_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_today_bookings(self):
        today = datetime.now().strftime('%Y-%m-%d')
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings
                WHERE booking_date = ? AND status = 'active'
                ORDER BY booking_time
            ''', (today,))
            return cursor.fetchall()
    
    def get_week_bookings(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT booking_date, COUNT(*) as count
                FROM bookings
                WHERE booking_date >= date('now') AND status = 'active'
                GROUP BY booking_date
                ORDER BY booking_date
            ''')
            return cursor.fetchall()
    
    def save_feedback(self, user_id, username, rating, comment):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (user_id, username, rating, comment)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, rating, comment))
            conn.commit()

db = Database()
