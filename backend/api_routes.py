"""
API Routes für JARVIS Control System
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

router = APIRouter()

# ============ PYDANTIC MODELS ============

class ControlCommand(BaseModel):
    command: Optional[str] = None
    mode: Optional[str] = None
    confirm: Optional[bool] = False

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = "user"

class TrainingConfig(BaseModel):
    mode: str = "intensive"
    epochs: int = 100

# ============ HEALTH & STATUS ============

@router.get("/status")
async def get_status():
    """Get current system status"""
    state = get_ai_state()
    return {
        **state,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "jarvis-ai-system",
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

@router.post("/control/command")
async def execute_command(cmd: ControlCommand):
    """Execute custom command"""
    if not cmd.command:
        raise HTTPException(status_code=400, detail="No command provided")
    
    # Hier könnten deine JARVIS AI Module integriert werden
    input_text = cmd.command
    output_text = f"Processed: {cmd.command}"
    confidence = 85
    processing_time = 45
    
    save_activity("COMMAND", processing_time, confidence, input_text, output_text)
    save_chat_message(input_text, output_text, confidence)
    
    return {
        "status": "success",
        "message": "Command executed",
        "input": input_text,
        "output": output_text,
        "confidence": confidence,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat()
    }

# ============ CHAT ============

@router.post("/chat")
async def chat(msg: ChatMessage):
    """Chat with JARVIS"""
    user_message = msg.message
    
    # Hier könnten deine JARVIS AI Module integriert werden
    ai_response = f"Response to: {user_message}"
    confidence = 82
    
    save_chat_message(user_message, ai_response, confidence)
    save_activity("CHAT", 50, confidence, user_message, ai_response)
    
    return {
        "status": "success",
        "user_message": user_message,
        "ai_response": ai_response,
        "confidence": confidence,
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

# ============ STATS & ANALYTICS ============

@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    status = get_ai_state()
    training = get_latest_training()
    
    return {
        "system": status,
        "training": training,
        "timestamp": datetime.now().isoformat()
    }
