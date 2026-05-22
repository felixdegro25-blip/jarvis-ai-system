"""
PC Server Connector
Verbindet JARVIS mit deinem lokalem PC-Server
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict
import asyncio

class PCServerConnector:
    """Connects to local PC Server (jarvis_server.py)"""
    
    def __init__(self, pc_server_url: str = "http://localhost:8765", 
                 pc_api_key: str = "DEIN_GEHEIMER_API_KEY"):
        """
        Initialize PC Server Connector
        
        Args:
            pc_server_url: URL of local PC server
            pc_api_key: API key for PC server
        """
        self.pc_server_url = pc_server_url
        self.pc_api_key = pc_api_key
        self.api_url = f"{pc_server_url}/api"
        self.headers = {
            "Authorization": f"Bearer {pc_api_key}",
            "Content-Type": "application/json"
        }
        self.is_connected = False
        self.check_connection()
    
    def check_connection(self) -> bool:
        """
        Check if PC server is reachable
        
        Returns:
            Connection status
        """
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=5
            )
            self.is_connected = response.status_code in [200, 401]
            if self.is_connected:
                print(f"🖥️  PC Server connected: {self.pc_server_url}")
            return self.is_connected
        except requests.exceptions.ConnectionError:
            self.is_connected = False
            print(f"⚠️  PC Server unreachable: {self.pc_server_url}")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            self.is_connected = False
            return False
    
    async def send_command(self, command: str) -> Dict:
        """
        Send command to PC server
        
        Args:
            command: Command to execute
        
        Returns:
            Response dict
        """
        if not self.is_connected:
            if not self.check_connection():
                return {
                    "status": "error",
                    "message": "PC Server not connected",
                    "timestamp": datetime.now().isoformat()
                }
        
        try:
            payload = {"command": command}
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "pc_response": result,
                    "timestamp": datetime.now().isoformat()
                }
            elif response.status_code == 401:
                return {
                    "status": "error",
                    "message": "PC Server: Invalid API key",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"PC Server error: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "PC Server timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_status(self) -> Dict:
        """
        Get PC server status
        
        Returns:
            Status dict
        """
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "pc_status": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Status code: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def execute_pc_action(self, action: str, **kwargs) -> Dict:
        """
        Execute PC action via command
        
        Args:
            action: Action type (screenshot, open_app, etc.)
            **kwargs: Additional parameters
        
        Returns:
            Response dict
        """
        commands = {
            "screenshot": "screenshot",
            "mute": "cmd volume mute",
            "lock": "cmd rundll32.exe user32.dll,LockWorkStation",
            "hibernate": "cmd rundll32.exe PowrProf.dll,SetSuspendState 1,1,0"
        }
        
        if action == "open_app":
            app = kwargs.get("app", "notepad")
            command = f"öffne {app}"
        elif action == "type_text":
            text = kwargs.get("text", "")
            command = f"tippe {text}"
        elif action in commands:
            command = commands[action]
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}",
                "timestamp": datetime.now().isoformat()
            }
        
        return await self.send_command(command)

# ============ SINGLETON ============
_pc_connector = None

def get_pc_connector(pc_server_url: str = "http://localhost:8765",
                    pc_api_key: str = "DEIN_GEHEIMER_API_KEY") -> PCServerConnector:
    """Get or create PC connector"""
    global _pc_connector
    if _pc_connector is None:
        _pc_connector = PCServerConnector(pc_server_url, pc_api_key)
    return _pc_connector
