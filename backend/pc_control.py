"""
PC Control & System Commands
Steuert deinen PC über JARVIS (Shutdown, Restart, etc.)
"""

import os
import sys
import subprocess
import psutil
from datetime import datetime
from typing import Optional

class PCController:
    """Control local PC via system commands"""
    
    def __init__(self):
        self.is_windows = sys.platform.startswith('win')
        self.is_linux = sys.platform.startswith('linux')
        self.is_mac = sys.platform.startswith('darwin')
        print(f"🖥️  PC Controller initialized - OS: {sys.platform}")
    
    def shutdown(self, delay_seconds: int = 0) -> dict:
        """
        Shutdown PC
        
        Args:
            delay_seconds: Delay before shutdown
        
        Returns:
            Status dict
        """
        try:
            if self.is_windows:
                if delay_seconds > 0:
                    cmd = f"shutdown /s /t {delay_seconds}"
                else:
                    cmd = "shutdown /s /t 0"
            elif self.is_linux or self.is_mac:
                if delay_seconds > 0:
                    cmd = f"shutdown -h +{delay_seconds // 60}"
                else:
                    cmd = "shutdown -h now"
            
            subprocess.run(cmd, shell=True)
            return {
                "status": "success",
                "action": "shutdown",
                "delay": delay_seconds,
                "message": f"PC will shutdown in {delay_seconds}s" if delay_seconds > 0 else "PC shutting down now",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error": str(e)
            }
    
    def restart(self, delay_seconds: int = 0) -> dict:
        """
        Restart PC
        
        Args:
            delay_seconds: Delay before restart
        
        Returns:
            Status dict
        """
        try:
            if self.is_windows:
                if delay_seconds > 0:
                    cmd = f"shutdown /r /t {delay_seconds}"
                else:
                    cmd = "shutdown /r /t 0"
            elif self.is_linux or self.is_mac:
                if delay_seconds > 0:
                    cmd = f"shutdown -r +{delay_seconds // 60}"
                else:
                    cmd = "shutdown -r now"
            
            subprocess.run(cmd, shell=True)
            return {
                "status": "success",
                "action": "restart",
                "delay": delay_seconds,
                "message": f"PC will restart in {delay_seconds}s" if delay_seconds > 0 else "PC restarting now",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error": str(e)
            }
    
    def sleep(self) -> dict:
        """
        Put PC to sleep
        """
        try:
            if self.is_windows:
                cmd = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
            elif self.is_mac:
                cmd = "osascript -e 'tell application \"System Events\" to sleep'"
            elif self.is_linux:
                cmd = "systemctl suspend"
            
            subprocess.run(cmd, shell=True)
            return {
                "status": "success",
                "action": "sleep",
                "message": "PC going to sleep",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error": str(e)
            }
    
    def open_application(self, app_name: str) -> dict:
        """
        Open application by name
        
        Args:
            app_name: Application name or path
        
        Returns:
            Status dict
        """
        try:
            if self.is_windows:
                os.startfile(app_name)
            else:
                subprocess.Popen(['open', app_name])
            
            return {
                "status": "success",
                "action": "open_app",
                "app": app_name,
                "message": f"Opening {app_name}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not open {app_name}",
                "error": str(e)
            }
    
    def get_system_info(self) -> dict:
        """
        Get system information
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "status": "success",
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_gb": round(memory.used / (1024**3), 2),
                    "memory_total_gb": round(memory.total / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "disk_used_gb": round(disk.used / (1024**3), 2),
                    "disk_total_gb": round(disk.total / (1024**3), 2),
                    "platform": sys.platform
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error": str(e)
            }
    
    def execute_command(self, command: str) -> dict:
        """
        Execute custom command
        
        WARNING: Use with caution!
        
        Args:
            command: Command to execute
        
        Returns:
            Command output
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "status": "success",
                "command": command,
                "output": result.stdout,
                "error": result.stderr if result.stderr else None,
                "return_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Command timeout",
                "error": "timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error": str(e)
            }

# ============ SINGLETON ============
_pc_controller = None

def get_pc_controller() -> PCController:
    """Get or create PC controller"""
    global _pc_controller
    if _pc_controller is None:
        _pc_controller = PCController()
    return _pc_controller
