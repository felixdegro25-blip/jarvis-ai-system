"""
Background AI Worker Thread
Verarbeitet KI-Anfragen und Training im Hintergrund
"""

import threading
import time
import random
from backend.database import save_system_status, save_training_data
from backend.config import settings

class AIWorkerState:
    """Global AI Worker State"""
    def __init__(self):
        self.status = "online"
        self.cpu = 0
        self.memory = 0
        self.gpu = 0
        self.temperature = 32
        self.is_training = False
        self.training_mode = "normal"
        self.current_epoch = 0
        self.start_time = time.time()
        self.uptime = 0

ai_state = AIWorkerState()

def ai_background_worker():
    """Background thread für KI Processing & Training"""
    print("🤖 AI Background Worker Started")
    
    epoch = 0
    
    while True:
        try:
            # Update every N seconds
            time.sleep(settings.AI_UPDATE_INTERVAL)
            
            # Calculate uptime
            ai_state.uptime = int(time.time() - ai_state.start_time)
            
            # Simuliere System Metrics (ersetze mit echten Werten)
            ai_state.cpu = min(100, random.uniform(20, 80))
            ai_state.memory = min(100, random.uniform(30, 70))
            ai_state.gpu = min(100, random.uniform(10, 60))
            ai_state.temperature = 32 + random.uniform(0, 25)
            
            # Speichere System Status
            save_system_status(
                ai_state.status,
                ai_state.cpu,
                ai_state.memory,
                ai_state.gpu,
                ai_state.temperature,
                ai_state.uptime
            )
            
            # Wenn Training aktiv ist
            if ai_state.is_training:
                epoch += 1
                accuracy = min(99, 50 + (epoch * 0.5) + random.uniform(-2, 2))
                loss = max(0.01, 1.0 - (epoch * 0.008))
                progress = min(100, int((epoch / 100) * 100))
                
                ai_state.current_epoch = epoch
                
                # Save to database
                save_training_data(
                    epoch,
                    accuracy,
                    loss,
                    progress,
                    True,
                    ai_state.training_mode
                )
                
                print(f"📊 Training - Epoch {epoch} | Accuracy: {accuracy:.2f}% | Loss: {loss:.4f}")
                
                # Stop training bei 100%
                if progress >= 100:
                    ai_state.is_training = False
                    epoch = 0
                    print("✅ Training completed!")
            
        except Exception as e:
            print(f"❌ AI Worker Error: {e}")
            time.sleep(1)

def start_ai_worker():
    """Start the AI background worker thread"""
    ai_thread = threading.Thread(target=ai_background_worker, daemon=True)
    ai_thread.start()
    return ai_thread

def set_training(enabled: bool, mode: str = "normal"):
    """Enable/disable training"""
    ai_state.is_training = enabled
    ai_state.training_mode = mode
    if enabled:
        print(f"🧠 Training started: {mode}")
    else:
        print(f"⏹️  Training stopped")

def get_ai_state():
    """Get current AI state"""
    return {
        "status": ai_state.status,
        "cpu": round(ai_state.cpu, 2),
        "memory": round(ai_state.memory, 2),
        "gpu": round(ai_state.gpu, 2),
        "temperature": round(ai_state.temperature, 1),
        "is_training": ai_state.is_training,
        "training_mode": ai_state.training_mode,
        "uptime": ai_state.uptime
    }
