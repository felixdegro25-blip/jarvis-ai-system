"""
Datenbank Management für JARVIS System
"""

import sqlite3
import os
from datetime import datetime
from backend.config import settings

def get_db_path():
    """Get database path and create directory if needed"""
    os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
    return settings.DATABASE_PATH

def init_database():
    """Initialize SQLite Database"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # System Status Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT DEFAULT 'online',
            cpu REAL DEFAULT 0,
            memory REAL DEFAULT 0,
            gpu REAL DEFAULT 0,
            temperature REAL DEFAULT 32,
            uptime INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Activity Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            processing_time INTEGER,
            confidence REAL,
            input_text TEXT,
            output_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Training Data Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            epoch INTEGER,
            accuracy REAL,
            loss REAL,
            progress INTEGER,
            is_training BOOLEAN DEFAULT 0,
            mode TEXT DEFAULT 'normal',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # AI Model Data Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT UNIQUE,
            model_data BLOB,
            accuracy REAL,
            parameters INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {db_path}")

# ============ DATABASE HELPER FUNCTIONS ============

def get_connection():
    """Get database connection"""
    return sqlite3.connect(get_db_path())

def dict_from_row(cursor_description, row):
    """Convert database row to dictionary"""
    return dict(zip([c[0] for c in cursor_description], row))

# ============ SYSTEM STATUS ============

def save_system_status(status, cpu, memory, gpu, temperature, uptime):
    """Save system status to database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO system_status (status, cpu, memory, gpu, temperature, uptime)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (status, cpu, memory, gpu, temperature, uptime))
    conn.commit()
    conn.close()

def get_latest_status():
    """Get latest system status"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT status, cpu, memory, gpu, temperature, uptime, timestamp
        FROM system_status
        ORDER BY id DESC LIMIT 1
    ''')
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else {}

# ============ ACTIVITY LOG ============

def save_activity(task, processing_time, confidence, input_text, output_text):
    """Save activity to database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activity_log (task, processing_time, confidence, input_text, output_text)
        VALUES (?, ?, ?, ?, ?)
    ''', (task, processing_time, confidence, input_text, output_text))
    conn.commit()
    conn.close()

def get_activity_history(limit=20):
    """Get activity history"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT task, processing_time, confidence, input_text, output_text, timestamp
        FROM activity_log
        ORDER BY id DESC LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

# ============ TRAINING DATA ============

def save_training_data(epoch, accuracy, loss, progress, is_training, mode='normal'):
    """Save training data"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO training_data (epoch, accuracy, loss, progress, is_training, mode)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (epoch, accuracy, loss, progress, is_training, mode))
    conn.commit()
    conn.close()

def get_latest_training():
    """Get latest training data"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT epoch, accuracy, loss, progress, is_training, mode, timestamp
        FROM training_data
        ORDER BY id DESC LIMIT 1
    ''')
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else {}

def get_training_history(limit=20):
    """Get training history"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT epoch, accuracy, loss, progress, mode, timestamp
        FROM training_data
        ORDER BY id DESC LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

# ============ CHAT HISTORY ============

def save_chat_message(user_message, ai_response, confidence):
    """Save chat message"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_message, ai_response, confidence)
        VALUES (?, ?, ?)
    ''', (user_message, ai_response, confidence))
    conn.commit()
    conn.close()

def get_chat_history(limit=20):
    """Get chat history"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_message, ai_response, confidence, timestamp
        FROM chat_history
        ORDER BY id DESC LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]
