"""
Task Scheduler für JARVIS
Speichert Aufgaben, Termine, Erinnerungen
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
from backend.database import get_connection

class TaskType(str, Enum):
    """Task Types"""
    REMINDER = "reminder"
    ALARM = "alarm"
    TASK = "task"
    MEETING = "meeting"
    DEADLINE = "deadline"

class TaskStatus(str, Enum):
    """Task Status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

def create_tables():
    """Create task-related tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tasks/Reminders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            type TEXT DEFAULT 'task',
            status TEXT DEFAULT 'pending',
            due_date DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            priority INTEGER DEFAULT 0,
            tags TEXT,
            notes TEXT
        )
    ''')
    
    # Reminders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            reminder_time DATETIME,
            message TEXT,
            sent BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')
    
    # Events/Calendar Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            start_time DATETIME,
            end_time DATETIME,
            location TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            tags TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Task scheduler tables created")

# ============ TASK FUNCTIONS ============

def create_task(title: str, description: str = "", task_type: str = "task", 
                due_date: Optional[str] = None, priority: int = 0) -> dict:
    """
    Create a new task
    
    Args:
        title: Task title
        description: Task description
        task_type: Type of task (task, reminder, alarm, meeting, deadline)
        due_date: Due date (ISO format)
        priority: Priority level (0-10)
    
    Returns:
        Task dict with ID
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, type, due_date, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, task_type, due_date, priority))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "task_id": task_id,
            "title": title,
            "due_date": due_date,
            "message": f"Task created: {title}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error": str(e)
        }

def get_tasks(status: str = None, limit: int = 20) -> List[dict]:
    """
    Get tasks
    
    Args:
        status: Filter by status (pending, completed, etc.)
        limit: Max results
    
    Returns:
        List of tasks
    """
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM tasks
                WHERE status = ?
                ORDER BY due_date ASC
                LIMIT ?
            ''', (status, limit))
        else:
            cursor.execute('''
                SELECT * FROM tasks
                ORDER BY due_date ASC
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    except Exception as e:
        print(f"❌ Error getting tasks: {e}")
        return []

def update_task_status(task_id: int, status: str) -> dict:
    """
    Update task status
    
    Args:
        task_id: Task ID
        status: New status
    
    Returns:
        Status dict
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        completed_at = datetime.now().isoformat() if status == "completed" else None
        
        cursor.execute('''
            UPDATE tasks
            SET status = ?, completed_at = ?
            WHERE id = ?
        ''', (status, completed_at, task_id))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "task_id": task_id,
            "new_status": status,
            "message": f"Task {task_id} updated to {status}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error": str(e)
        }

def create_reminder(task_id: int, reminder_time: str, message: str) -> dict:
    """
    Create reminder for task
    
    Args:
        task_id: Task ID
        reminder_time: When to remind (ISO format)
        message: Reminder message
    
    Returns:
        Status dict
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reminders (task_id, reminder_time, message)
            VALUES (?, ?, ?)
        ''', (task_id, reminder_time, message))
        
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "reminder_id": reminder_id,
            "task_id": task_id,
            "reminder_time": reminder_time,
            "message": f"Reminder created",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error": str(e)
        }

def get_pending_reminders() -> List[dict]:
    """
    Get pending reminders that should be sent
    
    Returns:
        List of reminders
    """
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            SELECT r.*, t.title
            FROM reminders r
            JOIN tasks t ON r.task_id = t.id
            WHERE r.sent = 0
            AND r.reminder_time <= ?
            ORDER BY r.reminder_time ASC
        ''', (now,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    except Exception as e:
        print(f"❌ Error getting reminders: {e}")
        return []

def mark_reminder_sent(reminder_id: int) -> dict:
    """
    Mark reminder as sent
    
    Args:
        reminder_id: Reminder ID
    
    Returns:
        Status dict
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reminders
            SET sent = 1
            WHERE id = ?
        ''', (reminder_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "reminder_id": reminder_id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def create_event(title: str, start_time: str, end_time: str = None, 
                 location: str = "", description: str = "") -> dict:
    """
    Create calendar event
    
    Args:
        title: Event title
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        location: Event location
        description: Event description
    
    Returns:
        Event dict
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (title, description, start_time, end_time, location)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, start_time, end_time, location))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "event_id": event_id,
            "title": title,
            "start_time": start_time,
            "message": f"Event created: {title}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error": str(e)
        }

def get_upcoming_events(days: int = 7) -> List[dict]:
    """
    Get upcoming events
    
    Args:
        days: Number of days ahead to check
    
    Returns:
        List of events
    """
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        future = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT * FROM events
            WHERE start_time BETWEEN ? AND ?
            ORDER BY start_time ASC
        ''', (now, future))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    except Exception as e:
        print(f"❌ Error getting events: {e}")
        return []
