"""
Improved API Routes mit besserem Error Handling,
Dependency Checks und stabilerer FastAPI Struktur
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import traceback
import logging

# ============================================
# LOGGER
# ============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jarvis-api")

# ============================================
# SAFE IMPORTS
# ============================================

try:
    from backend.database import (
        save_activity,
        save_chat_message,
        get_chat_history,
        get_activity_history,
        get_training_history,
        get_latest_status,
        get_latest_training
    )
except Exception as e:
    logger.error(f"Database import error: {e}")

try:
    from backend.ai_worker import get_ai_state, set_training, ai_state
except Exception as e:
    logger.error(f"AI Worker import error: {e}")

try:
    from backend.huggingface_ai import get_ai
except Exception as e:
    logger.error(f"HuggingFace import error: {e}")

try:
    from backend.pc_control import get_pc_controller
except Exception as e:
    logger.error(f"PC Control import error: {e}")

try:
    from backend.scheduler import (
        create_task,
        get_tasks,
        update_task_status,
        create_reminder,
        get_pending_reminders,
        mark_reminder_sent,
        create_event,
        get_upcoming_events,
        create_tables
    )
except Exception as e:
    logger.error(f"Scheduler import error: {e}")

try:
    from backend.auth_system import get_auth
except Exception as e:
    logger.error(f"Auth import error: {e}")

# ============================================
# ROUTER
# ============================================

router = APIRouter()

# ============================================
# INIT DATABASE TABLES
# ============================================

try:
    create_tables()
    logger.info("Scheduler tables initialized")
except Exception as e:
    logger.error(f"Failed to initialize tables: {e}")

# ============================================
# MODELS
# ============================================

class ControlCommand(BaseModel):
    command: Optional[str] = None
    mode: Optional[str] = "normal"
    confirm: Optional[bool] = False


class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = "user"
    context: Optional[List] = []


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


# ============================================
# AUTH HELPER
# ============================================

def verify_api_key(
    authorization: Optional[str] = Header(None)
):
    """
    Verify API Key

    Expected:
    Authorization: Bearer YOUR_KEY
    """

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    try:
        parts = authorization.split(" ")

        if len(parts) != 2:
            raise HTTPException(
                status_code=401,
                detail="Invalid Authorization format"
            )

        scheme, token = parts

        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid auth scheme"
            )

        auth = get_auth()

        is_valid, key_id, data = auth.verify_api_key(token)

        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired API key"
            )

        return key_id

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Auth error: {e}")

        raise HTTPException(
            status_code=500,
            detail="Authentication failed"
        )

# ============================================
# GLOBAL ERROR RESPONSE
# ============================================

def error_response(message: str, error: str = ""):
    return {
        "status": "error",
        "message": message,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# HEALTH
# ============================================

@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "jarvis-ai-system",
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# STATUS
# ============================================

@router.get("/status")
async def get_status():

    try:
        state = get_ai_state()

        return {
            "status": state.status,
            "training": state.training,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(traceback.format_exc())

        return error_response(
            "Failed to fetch status",
            str(e)
        )

# ============================================
# CONTROL START
# ============================================

@router.post("/control/start")
async def control_start(
    key_id: str = Depends(verify_api_key)
):

    try:
        ai_state.status = "online"

        save_activity(
            "START",
            10,
            100,
            "-",
            "System online"
        )

        return {
            "status": "success",
            "message": "JARVIS started",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(traceback.format_exc())

        return error_response(
            "Failed to start system",
            str(e)
        )

# ============================================
# CHAT
# ============================================

@router.post("/chat")
async def chat(
    msg: ChatMessage,
    key_id: str = Depends(verify_api_key)
):

    try:
        ai = get_ai()

        response = await ai.chat_with_context(
            msg.message,
            msg.context
        )

        ai_response = response.get(
            "response",
            "No response"
        )

        confidence = response.get(
            "confidence",
            0
        )

        save_chat_message(
            msg.message,
            ai_response,
            confidence
        )

        save_activity(
            "CHAT",
            50,
            confidence,
            msg.message,
            ai_response
        )

        return {
            "status": "success",
            "user_message": msg.message,
            "ai_response": ai_response,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logger.error(traceback.format_exc())

        return error_response(
            "Chat processing failed",
            str(e)
        )

# ============================================
# CHAT HISTORY
# ============================================

@router.get("/chat/history")
async def get_chat_log(
    limit: int = 20,
    key_id: str = Depends(verify_api_key)
):

    try:
        history = get_chat_history(limit)

        return {
            "count": len(history),
            "messages": history,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logger.error(traceback.format_exc())

        return error_response(
            "Failed to load chat history",
            str(e)
        )

# ============================================
# PC COMMANDS
# ============================================

@router.post("/pc/command")
async def pc_command(
    cmd: PCCommand,
    key_id: str = Depends(verify_api_key)
):

    try:

        pc = get_pc_controller()

        if cmd.action == "shutdown":
            result = pc.shutdown(cmd.delay)

        elif cmd.action == "restart":
            result = pc.restart(cmd.delay)

        elif cmd.action == "sleep":
            result = pc.sleep()

        elif cmd.action == "open_app":

            if not cmd.app_name:
                raise ValueError(
                    "app_name required"
                )

            result = pc.open_application(
                cmd.app_name
            )

        elif cmd.action == "execute_command":

            if not cmd.command:
                raise ValueError(
                    "command required"
                )

            result = pc.execute_command(
                cmd.command
            )

        elif cmd.action == "info":
            result = pc.get_system_info()

        else:
            raise ValueError(
                f"Unknown action: {cmd.action}"
            )

        save_activity(
            f"PC_{cmd.action}",
            0,
            100,
            cmd.action,
            str(result)
        )

        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logger.error(traceback.format_exc())

        return error_response(
            "PC command failed",
            str(e)
        )

# ============================================
# TASKS
# ============================================

@router.post("/tasks")
async def create_new_task(
    task: TaskCreate,
    key_id: str = Depends(verify_api_key)
):

    try:

        result = create_task(
            task.title,
            task.description,
            task.task_type,
            task.due_date,
            task.priority
        )

        return {
            "status": "success",
            "task": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logger.error(traceback.format_exc())

        return error_response(
            "Task creation failed",
            str(e)
        )

# ============================================
# GET TASKS
# ============================================

@router.get("/tasks")
async def get_all_tasks(
    status: Optional[str] = None,
    limit: int = 20,
    key_id: str = Depends(verify_api_key)
):

    try:

        tasks = get_tasks(status, limit)

        return {
            "count": len(tasks),
            "tasks": tasks,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logger.error(traceback.format_exc())

        return error_response(
            "Failed to fetch tasks",
            str(e)
        )

# ============================================
# TRAINING
# ============================================

@router.post("/training/start")
async def start_training(
    cmd: ControlCommand,
    key_id: str = Depends(verify_api_key)
):

    try:

        set_training(
            True,
            cmd.mode
        )

        return {
            "status": "success",
            "mode": cmd.mode,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logger.error(traceback.format_exc())

        return error_response(
            "Training failed",
            str(e)
        )

# ============================================
# SYSTEM STATS
# ============================================

@router.get("/stats")
async def get_stats(
    key_id: str = Depends(verify_api_key)
):

    try:

        tasks = get_tasks(limit=100)

        return {
            "tasks_total": len(tasks),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logger.error(traceback.format_exc())

        return error_response(
            "Failed to load stats",
            str(e)
        )