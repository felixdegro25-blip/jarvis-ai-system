"""
Updated API Routes mit Authentifizierung & PC Server Integration
JARVIS Control System - Komplette API
"""

from fastapi import APIRouter, HTTPException, Header
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
from backend.auth_system import get_auth
from backend.pc_server_connector import get_pc_connector
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
    action: str
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

class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    permissions: Optional[str] = "all"
    expiry_days: Optional[int] = 365

class DeviceRegister(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    ip_address: Optional[str] = ""

# ============ AUTHENTICATION HELPER ============

def verify_api_key(authorization: Optional[str] = Header(None)):
    """
    Verify API key from Authorization header
    
    Expected format: "Bearer key_id.secret"
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    try:
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(status_code=401, detail="Invalid Authorization format")
        
        full_key = parts[1]
        auth = get_auth()
        is_valid, key_id, data = auth.verify_api_key(full_key)
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid or expired API key")
        
        return key_id
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# ============ HEALTH & STATUS ============

@router.get("/status")
async def get_status(authorization: Optional[str] = Header(None)):
    """Get current system status"""
    try:
        key_id = verify_api_key(authorization)
    except HTTPException:
        # Allow unauthenticated access for health check
        pass
    
    state = get_ai_state()
    pc = get_pc_controller().get_system_info()
    return {
        **state,
        "pc_info": pc.get('system', {}),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health():
    """Health check (no auth required)"""
    return {
        "status": "healthy",
        "service": "jarvis-ai-system",
        "ai": "huggingface",
        "timestamp": datetime.now().isoformat()
    }

# ============ ACTIVITY ============

@router.get("/activity")
async def get_activity(authorization: Optional[str] = Header(None)):
    """Get current activity"""
    key_id = verify_api_key(authorization)
    return {
        "current_task": "System ready",
        "processing_time": 0,
        "confidence": 0,
        "input": "-",
        "output": "-",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/activity/history")
async def get_activity_log(authorization: Optional[str] = Header(None), limit: int = 20):
    """Get activity history"""
    key_id = verify_api_key(authorization)
    history = get_activity_history(limit)
    return {
        "count": len(history),
        "activities": history,
        "timestamp": datetime.now().isoformat()
    }

# ============ TRAINING ============

@router.get("/training")
async def get_training(authorization: Optional[str] = Header(None)):
    """Get training progress"""
    key_id = verify_api_key(authorization)
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
async def get_training_log(authorization: Optional[str] = Header(None), limit: int = 20):
    """Get training history"""
    key_id = verify_api_key(authorization)
    history = get_training_history(limit)
    return {
        "count": len(history),
        "sessions": history,
        "timestamp": datetime.now().isoformat()
    }

# ============ CONTROL ENDPOINTS ============

@router.post("/control/start")
async def control_start(authorization: Optional[str] = Header(None)):
    """Start JARVIS"""
    key_id = verify_api_key(authorization)
    ai_state.status = "online"
    save_activity("START", 10, 100, "-", "System online")
    get_auth().log_access(key_id, "/control/start", "POST", 200)
    return {
        "status": "success",
        "message": "JARVIS started ✅",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/control/pause")
async def control_pause(authorization: Optional[str] = Header(None)):
    """Pause JARVIS"""
    key_id = verify_api_key(authorization)
    ai_state.status = "paused"
    save_activity("PAUSE", 5, 0, "-", "System paused")
    get_auth().log_access(key_id, "/control/pause", "POST", 200)
    return {
        "status": "success",
        "message": "JARVIS paused ⏸",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/control/training")
async def control_training(cmd: ControlCommand, authorization: Optional[str] = Header(None)):
    """Start Training Mode"""
    key_id = verify_api_key(authorization)
    mode = cmd.mode or "intensive"
    set_training(True, mode)
    save_activity("TRAINING", 0, 0, "-", f"Training started: {mode}")
    get_auth().log_access(key_id, "/control/training", "POST", 200)
    return {
        "status": "success",
        "message": f"Training started in {mode} mode 🧠",
        "mode": mode,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/control/shutdown")
async def control_shutdown(cmd: ControlCommand, authorization: Optional[str] = Header(None)):
    """Shutdown JARVIS"""
    key_id = verify_api_key(authorization)
    if not cmd.confirm:
        return {
            "status": "error",
            "message": "Shutdown not confirmed",
            "timestamp": datetime.now().isoformat()
        }
    
    ai_state.status = "offline"
    save_activity("SHUTDOWN", 0, 0, "-", "System offline")
    get_auth().log_access(key_id, "/control/shutdown", "POST", 200)
    return {
        "status": "success",
        "message": "JARVIS shutdown ⏹",
        "timestamp": datetime.now().isoformat()
    }

# ============ AI CHAT (HUGGING FACE) ============

@router.post("/chat")
async def chat(msg: ChatMessage, authorization: Optional[str] = Header(None)):
    """Chat with JARVIS AI (Powered by Hugging Face)"""
    key_id = verify_api_key(authorization)
    
    try:
        ai = get_ai()
        user_message = msg.message
        
        response = await ai.chat_with_context(user_message, msg.context)
        
        if response['status'] == 'error':
            ai_response = response['response']
            confidence = 0
        else:
            ai_response = response['response']
            confidence = response.get('confidence', 0)
        
        save_chat_message(user_message, ai_response, confidence)
        save_activity("CHAT", 50, confidence, user_message, ai_response)
        get_auth().log_access(key_id, "/chat", "POST", 200)
        
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
        get_auth().log_access(key_id, "/chat", "POST", 500)
        return {
            "status": "error",
            "message": f"Chat error: {str(e)}",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/chat/history")
async def get_chat_log(authorization: Optional[str] = Header(None), limit: int = 20):
    """Get chat history"""
    key_id = verify_api_key(authorization)
    history = get_chat_history(limit)
    get_auth().log_access(key_id, "/chat/history", "GET", 200)
    return {
        "count": len(history),
        "messages": history,
        "timestamp": datetime.now().isoformat()
    }

# ============ PC CONTROL (via PC Server) ============

@router.post("/pc/command")
async def pc_command(cmd: PCCommand, authorization: Optional[str] = Header(None)):
    """
    Execute PC control command via local PC Server
    """
    key_id = verify_api_key(authorization)
    
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
        get_auth().log_access(key_id, "/pc/command", "POST", 200)
        return result
    
    except Exception as e:
        get_auth().log_access(key_id, "/pc/command", "POST", 500)
        return {
            "status": "error",
            "message": str(e),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/pc/info")
async def pc_info(authorization: Optional[str] = Header(None)):
    """Get PC system information"""
    key_id = verify_api_key(authorization)
    pc = get_pc_controller()
    get_auth().log_access(key_id, "/pc/info", "GET", 200)
    return pc.get_system_info()

# ============ TASKS & REMINDERS ============

@router.post("/tasks")
async def create_new_task(task: TaskCreate, authorization: Optional[str] = Header(None)):
    """Create new task"""
    key_id = verify_api_key(authorization)
    result = create_task(
        task.title,
        task.description,
        task.task_type,
        task.due_date,
        task.priority
    )
    save_activity("CREATE_TASK", 0, 100, task.title, f"Task created")
    get_auth().log_access(key_id, "/tasks", "POST", 200)
    return result

@router.get("/tasks")
async def get_all_tasks(authorization: Optional[str] = Header(None), status: Optional[str] = None, limit: int = 20):
    """Get all tasks"""
    key_id = verify_api_key(authorization)
    tasks = get_tasks(status, limit)
    get_auth().log_access(key_id, "/tasks", "GET", 200)
    return {
        "count": len(tasks),
        "tasks": tasks,
        "timestamp": datetime.now().isoformat()
    }

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, status: str, authorization: Optional[str] = Header(None)):
    """Update task status"""
    key_id = verify_api_key(authorization)
    result = update_task_status(task_id, status)
    get_auth().log_access(key_id, f"/tasks/{task_id}", "PUT", 200)
    return result

@router.post("/reminders")
async def create_new_reminder(reminder: ReminderCreate, authorization: Optional[str] = Header(None)):
    """Create new reminder"""
    key_id = verify_api_key(authorization)
    result = create_reminder(reminder.task_id, reminder.reminder_time, reminder.message)
    get_auth().log_access(key_id, "/reminders", "POST", 200)
    return result

@router.get("/reminders/pending")
async def get_pending(authorization: Optional[str] = Header(None)):
    """Get pending reminders"""
    key_id = verify_api_key(authorization)
    reminders = get_pending_reminders()
    
    for reminder in reminders:
        mark_reminder_sent(reminder['id'])
    
    get_auth().log_access(key_id, "/reminders/pending", "GET", 200)
    return {
        "count": len(reminders),
        "reminders": reminders,
        "timestamp": datetime.now().isoformat()
    }

# ============ EVENTS / CALENDAR ============

@router.post("/events")
async def create_new_event(event: EventCreate, authorization: Optional[str] = Header(None)):
    """Create calendar event"""
    key_id = verify_api_key(authorization)
    result = create_event(
        event.title,
        event.start_time,
        event.end_time,
        event.location,
        event.description
    )
    get_auth().log_access(key_id, "/events", "POST", 200)
    return result

@router.get("/events/upcoming")
async def get_upcoming(authorization: Optional[str] = Header(None), days: int = 7):
    """Get upcoming events"""
    key_id = verify_api_key(authorization)
    events = get_upcoming_events(days)
    get_auth().log_access(key_id, "/events/upcoming", "GET", 200)
    return {
        "count": len(events),
        "events": events,
        "timestamp": datetime.now().isoformat()
    }

# ============ AUTHENTICATION / API KEYS ============

@router.post("/auth/generate-key")
async def generate_api_key(key_data: APIKeyCreate):
    """
    Generate new API key
    
    WARNING: Only do this on local network!
    """
    auth = get_auth()
    result = auth.generate_api_key(
        key_data.name,
        key_data.description,
        key_data.permissions,
        key_data.expiry_days
    )
    return result

@router.get("/auth/keys")
async def list_api_keys(authorization: Optional[str] = Header(None)):
    """List all API keys (only key metadata, not secrets)"""
    key_id = verify_api_key(authorization)
    auth = get_auth()
    keys = auth.get_all_keys(active_only=True)
    get_auth().log_access(key_id, "/auth/keys", "GET", 200)
    return {
        "count": len(keys),
        "keys": keys,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/auth/register-device")
async def register_device(device: DeviceRegister, authorization: Optional[str] = Header(None)):
    """Register connected device"""
    key_id = verify_api_key(authorization)
    auth = get_auth()
    result = auth.register_device(
        device.device_id,
        device.device_name,
        device.device_type,
        key_id,
        device.ip_address
    )
    get_auth().log_access(key_id, "/auth/register-device", "POST", 200)
    return result

@router.get("/auth/devices")
async def list_devices(authorization: Optional[str] = Header(None)):
    """List connected devices"""
    key_id = verify_api_key(authorization)
    auth = get_auth()
    devices = auth.get_connected_devices()
    get_auth().log_access(key_id, "/auth/devices", "GET", 200)
    return {
        "count": len(devices),
        "devices": devices,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/auth/access-logs")
async def get_access_logs(authorization: Optional[str] = Header(None), limit: int = 50):
    """Get access logs"""
    key_id = verify_api_key(authorization)
    auth = get_auth()
    logs = auth.get_access_logs(key_id, limit)
    get_auth().log_access(key_id, "/auth/access-logs", "GET", 200)
    return {
        "count": len(logs),
        "logs": logs,
        "timestamp": datetime.now().isoformat()
    }

# ============ STATS & ANALYTICS ============

@router.get("/stats")
async def get_stats(authorization: Optional[str] = Header(None)):
    """Get system statistics"""
    key_id = verify_api_key(authorization)
    status = get_ai_state()
    training = get_latest_training()
    tasks = get_tasks(limit=100)
    pending_reminders = get_pending_reminders()
    get_auth().log_access(key_id, "/stats", "GET", 200)
    
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
