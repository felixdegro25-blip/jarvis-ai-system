"""
API Routes für JARVIS Control System
Mit Hugging Face AI, PC Control & Task Scheduler
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.database import (
    save_activity,
    save_chat_message,
    get_chat_history,
    get_activity_history,
    get_training_history,
    get_latest_status,
    get_latest_training
)
from backend.ai_worker import get_ai_state, set_training, ai_state
from backend.huggingface_ai import get_ai
from backend.pc_control import get_pc_controller
from backend.scheduler import (
    create_task, get_tasks, update_task_status,
    create_reminder, get_pending_reminders, mark_reminder_sent,
    create_event, get_upcoming_events, create_tables
)
import os

router = APIRouter()

# Initialize scheduler tables on startup
try:
    create_tables()
except:
    pass

# ============ PYDANTIC MODELS ============

class ControlCommand(BaseModel):
    command: Optional[str] = None
    mode: Optional[str] = None
    confirm: Optional[bool] = False

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = "user"
    context: Optional[list] = None

class PCCommand(BaseModel):
    action: str  # shutdown, restart, sleep, open_app, execute_command
    delay: Optional[int] = 0
    app_name: Optional[str] = None
    command: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    task_type: Optional[str] = "task"
    due_date: Optional[str] = None
    priority: Optional[int] = 0

class ReminderCreate(BaseModel):
    task_id: int
    reminder_time: str
    message: str

class EventCreate(BaseModel):
    title: str
    start_time: str
    end_time: Optional[str] = None
    location: Optional[str] = ""
    description: Optional[str] = ""

# ============ HEALTH & STATUS ============

@router.get("/status")
async def get_status():
    """Get current system status"""
    state = get_ai_state()
    pc = get_pc_controller().get_system_info()
    return {
        **state,
        "pc_info": pc.get('system', {}),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "jarvis-ai-system",
        "ai": "huggingface",
        "timestamp": datetime.now().isoformat()
    }

# ============ ACTIVITY ============

@router.get("/activity")
async def get_activity():
    """Get current activity"""
    return {
        "current_task": "System ready",
        "processing_time": 0,
        "confidence": 0,
        "input": "-",
        "output": "-",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/activity/history")
async def get_activity_log(limit: int = 20):
    """Get activity history"""
    history = get_activity_history(limit)
    return {
        "count": len(history),
        "activities": history,
        "timestamp": datetime.now().isoformat()
    }

# ============ TRAINING ============

@router.get("/training")
async def get_training():
    """Get training progress"""
    training_data = get_latest_training()
    return {
        "progress": training_data.get("progress", 0),
        "epochs": training_data.get("epoch", 0),
        "accuracy": training_data.get("accuracy", 0),
        "loss": training_data.get("loss", 0),
        "is_training": training_data.get("is_training", False),
        "mode": training_data.get("mode", "normal"),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/training/history")
async def get_training_log(limit: int = 20):
    """Get training history"""
    history = get_training_history(limit)
    return {
        "count": len(history),
        "sessions": history,
        "timestamp": datetime.now().isoformat()
    }

# ============ CONTROL ENDPOINTS ============

@router.post("/control/start")
async def control_start():
    """Start JARVIS"""
    ai_state.status = "online"
    save_activity("START", 10, 100, "-", "System online")
    return {
        "status": "success",
        "message": "JARVIS started ✅",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/control/pause")
async def control_pause():
    """Pause JARVIS"""
    ai_state.status = "paused"
    save_activity("PAUSE", 5, 0, "-", "System paused")
    return {
        "status": "success",
        "message": "JARVIS paused ⏸",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/control/training")
async def control_training(cmd: ControlCommand):
    """Start Training Mode"""
    mode = cmd.mode or "intensive"
    set_training(True, mode)
    save_activity("TRAINING", 0, 0, "-", f"Training started: {mode}")
    return {
        "status": "success",
        "message": f"Training started in {mode} mode 🧠",
        "mode": mode,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/control/shutdown")
async def control_shutdown(cmd: ControlCommand):
    """Shutdown JARVIS"""
    if not cmd.confirm:
        return {
            "status": "error",
            "message": "Shutdown not confirmed",
            "timestamp": datetime.now().isoformat()
        }
    
    ai_state.status = "offline"
    save_activity("SHUTDOWN", 0, 0, "-", "System offline")
    return {
        "status": "success",
        "message": "JARVIS shutdown ⏹",
        "timestamp": datetime.now().isoformat()
    }

# ============ AI CHAT (HUGGING FACE) ============

@router.post("/chat")
async def chat(msg: ChatMessage):
    """Chat with JARVIS AI (Powered by Hugging Face)"""
    try:
        ai = get_ai()
        user_message = msg.message
        
        # Get AI response
        response = await ai.chat_with_context(user_message, msg.context)
        
        if response['status'] == 'error':
            ai_response = response['response']
            confidence = 0
        else:
            ai_response = response['response']
            confidence = response.get('confidence', 0)
        
        # Save to database
        save_chat_message(user_message, ai_response, confidence)
        save_activity("CHAT", 50, confidence, user_message, ai_response)
        
        # Try to extract intent for PC commands
        intent = await ai.extract_intent(user_message)
        
        return {
            "status": "success",
            "user_message": user_message,
            "ai_response": ai_response,
            "confidence": confidence,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Chat error: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/chat/history")
async def get_chat_log(limit: int = 20):
    """Get chat history"""
    history = get_chat_history(limit)
    return {
        "count": len(history),
        "messages": history,
        "timestamp": datetime.now().isoformat()
    }

# ============ PC CONTROL ============

@router.post("/pc/command")
async def pc_command(cmd: PCCommand):
    """
    Execute PC control command
    
    Actions:
    - shutdown: Shutdown PC
    - restart: Restart PC
    - sleep: Sleep mode
    - open_app: Open application
    - execute_command: Execute custom command
    - info: Get system info
    """
    try:
        pc = get_pc_controller()
        
        if cmd.action == "shutdown":
            result = pc.shutdown(cmd.delay or 0)
        elif cmd.action == "restart":
            result = pc.restart(cmd.delay or 0)
        elif cmd.action == "sleep":
            result = pc.sleep()
        elif cmd.action == "open_app":
            if not cmd.app_name:
                raise ValueError("app_name required")
            result = pc.open_application(cmd.app_name)
        elif cmd.action == "execute_command":
            if not cmd.command:
                raise ValueError("command required")
            result = pc.execute_command(cmd.command)
        elif cmd.action == "info":
            result = pc.get_system_info()
        else:
            raise ValueError(f"Unknown action: {cmd.action}")
        
        save_activity(f"PC_{cmd.action}", 0, 100, cmd.action, str(result))
        return result
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/pc/info")
async def pc_info():
    """Get PC system information"""
    pc = get_pc_controller()
    return pc.get_system_info()

# ============ TASKS & REMINDERS ============

@router.post("/tasks")
async def create_new_task(task: TaskCreate):
    """Create new task"""
    result = create_task(
        task.title,
        task.description,
        task.task_type,
        task.due_date,
        task.priority
    )
    save_activity("CREATE_TASK", 0, 100, task.title, f"Task created")
    return result

@router.get("/tasks")
async def get_all_tasks(status: Optional[str] = None, limit: int = 20):
    """Get all tasks"""
    tasks = get_tasks(status, limit)
    return {
        "count": len(tasks),
        "tasks": tasks,
        "timestamp": datetime.now().isoformat()
    }

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, status: str):
    """Update task status"""
    result = update_task_status(task_id, status)
    return result

@router.post("/reminders")
async def create_new_reminder(reminder: ReminderCreate):
    """Create new reminder"""
    result = create_reminder(reminder.task_id, reminder.reminder_time, reminder.message)
    return result

@router.get("/reminders/pending")
async def get_pending():
    """Get pending reminders"""
    reminders = get_pending_reminders()
    
    # Mark as sent
    for reminder in reminders:
        mark_reminder_sent(reminder['id'])
    
    return {
        "count": len(reminders),
        "reminders": reminders,
        "timestamp": datetime.now().isoformat()
    }

# ============ EVENTS / CALENDAR ============

@router.post("/events")
async def create_new_event(event: EventCreate):
    """Create calendar event"""
    result = create_event(
        event.title,
        event.start_time,
        event.end_time,
        event.location,
        event.description
    )
    return result

@router.get("/events/upcoming")
async def get_upcoming(days: int = 7):
    """Get upcoming events"""
    events = get_upcoming_events(days)
    return {
        "count": len(events),
        "events": events,
        "timestamp": datetime.now().isoformat()
    }

# ============ STATS & ANALYTICS ============

@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    status = get_ai_state()
    training = get_latest_training()
    tasks = get_tasks(limit=100)
    pending_reminders = get_pending_reminders()
    
    return {
        "system": status,
        "training": training,
        "tasks": {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.get('status') == 'pending']),
            "completed": len([t for t in tasks if t.get('status') == 'completed'])
        },
        "reminders_pending": len(pending_reminders),
        "timestamp": datetime.now().isoformat()
    }
