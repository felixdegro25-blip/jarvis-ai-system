"""
JARVIS PC Agent
Runs on your local PC and communicates with main JARVIS server

Usage:
    python jarvis_pc_agent.py
    
Or run: jarvis_pc_agent.bat
"""

import requests
import time
import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Optional
import threading

class JarvisPCAgent:
    """Local PC Agent for JARVIS"""
    
    def __init__(self, server_url: str = "http://localhost:5000", 
                 api_key: str = "jarvis-pc-agent-key"):
        """
        Initialize PC Agent
        
        Args:
            server_url: JARVIS server URL (local or remote)
            api_key: API key for authentication
        """
        self.server_url = server_url
        self.api_key = api_key
        self.api_base = f"{server_url}/api"
        self.running = True
        self.poll_interval = 5  # Check server every 5 seconds
        
        print("\n" + "="*60)
        print("🖥️  JARVIS PC AGENT")
        print("="*60)
        print(f"🔗 Server: {self.server_url}")
        print(f"🔑 API Key: {self.api_key[:20]}...")
        print(f"⏱️  Poll Interval: {self.poll_interval}s")
        print("="*60 + "\n")
        
        self.check_server_connection()
    
    def check_server_connection(self):
        """Check if server is reachable"""
        try:
            response = requests.get(f"{self.server_url}", timeout=5)
            if response.status_code == 200:
                print("✅ Connected to JARVIS server")
                return True
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Could not connect to {self.server_url}")
            print("   Make sure the server is running!")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_pc_info(self) -> dict:
        """Get PC system information"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "timestamp": datetime.now().isoformat()
            }
        except:
            return {}
    
    def report_status(self):
        """Report PC status to server"""
        try:
            pc_info = self.get_pc_info()
            payload = {
                "agent_status": "online",
                "pc_info": pc_info,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_base}/pc/info",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Status reported - CPU: {pc_info.get('cpu_percent', 0):.1f}% | "
                      f"Memory: {pc_info.get('memory_percent', 0):.1f}%")
        
        except Exception as e:
            print(f"❌ Error reporting status: {e}")
    
    def check_pending_commands(self):
        """Check if server has pending commands for PC"""
        try:
            response = requests.get(
                f"{self.api_base}/pc/pending",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                commands = data.get('commands', [])
                
                if commands:
                    print(f"📋 {len(commands)} pending command(s)")
                    
                    for cmd in commands:
                        self.execute_command(cmd)
        
        except requests.exceptions.ConnectionError:
            print("⚠️  Server unreachable")
        except Exception as e:
            print(f"❌ Error checking commands: {e}")
    
    def execute_command(self, cmd: dict):
        """
        Execute command from server
        
        Args:
            cmd: Command dict with action, parameters, etc.
        """
        try:
            action = cmd.get('action')
            params = cmd.get('params', {})
            cmd_id = cmd.get('id')
            
            print(f"\n📨 Command received: {action}")
            
            result = None
            
            if action == "shutdown":
                delay = params.get('delay', 0)
                if sys.platform.startswith('win'):
                    os.system(f"shutdown /s /t {delay}")
                else:
                    os.system(f"shutdown -h +{delay // 60}")
                result = "Shutting down..."
                print("🔴 PC shutdown initiated")
            
            elif action == "restart":
                delay = params.get('delay', 0)
                if sys.platform.startswith('win'):
                    os.system(f"shutdown /r /t {delay}")
                else:
                    os.system(f"shutdown -r +{delay // 60}")
                result = "Restarting..."
                print("🔄 PC restart initiated")
            
            elif action == "sleep":
                if sys.platform.startswith('win'):
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                else:
                    os.system("systemctl suspend")
                result = "Going to sleep"
                print("😴 PC sleep initiated")
            
            elif action == "open_app":
                app = params.get('app')
                if sys.platform.startswith('win'):
                    os.startfile(app)
                else:
                    subprocess.Popen(['open', app])
                result = f"Opening {app}"
                print(f"🚀 Opening {app}")
            
            elif action == "execute_command":
                command = params.get('command')
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                print(f"⚙️  Executed: {command}")
            
            elif action == "message":
                message = params.get('message')
                print(f"\n💬 Message from JARVIS: {message}\n")
                result = "Message received"
            
            else:
                print(f"❓ Unknown action: {action}")
                result = "Unknown action"
            
            # Report result back to server
            self.report_command_result(cmd_id, action, result)
        
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            self.report_command_result(cmd_id, action, f"Error: {e}")
    
    def report_command_result(self, cmd_id: str, action: str, result: str):
        """
        Report command execution result to server
        
        Args:
            cmd_id: Command ID
            action: Action executed
            result: Result/output
        """
        try:
            payload = {
                "command_id": cmd_id,
                "action": action,
                "result": str(result),
                "timestamp": datetime.now().isoformat()
            }
            
            requests.post(
                f"{self.api_base}/pc/command-result",
                json=payload,
                timeout=5
            )
            print(f"✅ Result reported to server")
        
        except Exception as e:
            print(f"⚠️  Could not report result: {e}")
    
    def run(self):
        """Main loop - runs continuously"""
        print("🚀 PC Agent running...\n")
        
        try:
            while self.running:
                try:
                    # Report status
                    self.report_status()
                    
                    # Check for pending commands
                    self.check_pending_commands()
                    
                    # Sleep before next check
                    time.sleep(self.poll_interval)
                
                except KeyboardInterrupt:
                    print("\n\n⏹️  Agent stopped by user")
                    self.running = False
                except Exception as e:
                    print(f"❌ Error in main loop: {e}")
                    time.sleep(5)
        
        except KeyboardInterrupt:
            print("\n⏹️  Agent shutting down...")
        
        finally:
            print("✅ PC Agent stopped")

# ============ MAIN ============

if __name__ == "__main__":
    # Configuration
    SERVER_URL = os.getenv('JARVIS_SERVER_URL', 'http://localhost:5000')
    API_KEY = os.getenv('JARVIS_API_KEY', 'jarvis-pc-agent-key')
    
    # Create and run agent
    agent = JarvisPCAgent(server_url=SERVER_URL, api_key=API_KEY)
    agent.run()
