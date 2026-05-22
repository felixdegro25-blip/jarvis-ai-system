"""
Authentifizierungs-System für JARVIS
API Key Verwaltung & Zugriffskontrolle
"""

import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from backend.database import get_connection
import os

class AuthSystem:
    """Manage API Keys and Authentication"""
    
    def __init__(self):
        self.init_auth_tables()
    
    def init_auth_tables(self):
        """Initialize authentication tables"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # API Keys Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT UNIQUE NOT NULL,
                key_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME,
                is_active BOOLEAN DEFAULT 1,
                permissions TEXT DEFAULT 'all',
                rate_limit INTEGER DEFAULT 1000,
                expiry_date DATETIME
            )
        ''')
        
        # Access Control Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status INTEGER,
                ip_address TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (key_id) REFERENCES api_keys(key_id)
            )
        ''')
        
        # Connected Devices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connected_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                device_name TEXT NOT NULL,
                device_type TEXT,
                api_key_id TEXT NOT NULL,
                ip_address TEXT,
                status TEXT DEFAULT 'online',
                last_seen DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (api_key_id) REFERENCES api_keys(key_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Auth tables initialized")
    
    def generate_api_key(self, name: str, description: str = "", 
                        permissions: str = "all", expiry_days: int = 365) -> Dict:
        """
        Generate new API Key
        
        Args:
            name: Name for the key
            description: Description
            permissions: Comma-separated permissions (all, chat, pc_control, tasks, etc.)
            expiry_days: Days until expiry
        
        Returns:
            Dict with key_id and full_key (show only once!)
        """
        try:
            # Generate random key
            raw_key = secrets.token_urlsafe(32)
            key_id = f"jarvis_{secrets.token_hex(8)}"
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
            
            expiry_date = datetime.now() + timedelta(days=expiry_days)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_keys (key_id, key_hash, name, description, permissions, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (key_id, key_hash, name, description, permissions, expiry_date.isoformat()))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "key_id": key_id,
                "full_key": f"{key_id}.{raw_key}",
                "message": "⚠️  SAVE THIS KEY SAFELY! You won't see it again!",
                "created_at": datetime.now().isoformat(),
                "expires_at": expiry_date.isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "error": str(e)
            }
    
    def verify_api_key(self, full_key: str) -> tuple[bool, Optional[str], Dict]:
        """
        Verify API Key
        
        Args:
            full_key: Full key in format "key_id.secret"
        
        Returns:
            (is_valid, key_id, key_data)
        """
        try:
            parts = full_key.split('.')
            if len(parts) != 2:
                return False, None, {"error": "Invalid key format"}
            
            key_id, secret = parts
            key_hash = hashlib.sha256(secret.encode()).hexdigest()
            
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM api_keys
                WHERE key_id = ? AND key_hash = ? AND is_active = 1
            ''', (key_id, key_hash))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, None, {"error": "Invalid or inactive key"}
            
            result_dict = dict(result)
            
            # Check expiry
            if result_dict['expiry_date']:
                expiry = datetime.fromisoformat(result_dict['expiry_date'])
                if datetime.now() > expiry:
                    conn.close()
                    return False, None, {"error": "Key expired"}
            
            # Update last_used
            cursor.execute('''
                UPDATE api_keys SET last_used = ? WHERE key_id = ?
            ''', (datetime.now().isoformat(), key_id))
            conn.commit()
            conn.close()
            
            return True, key_id, result_dict
        
        except Exception as e:
            return False, None, {"error": str(e)}
    
    def get_all_keys(self, active_only: bool = True) -> List[Dict]:
        """
        Get all API keys
        
        Args:
            active_only: Only show active keys
        
        Returns:
            List of key dicts (without hashes)
        """
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute('SELECT * FROM api_keys WHERE is_active = 1 ORDER BY created_at DESC')
            else:
                cursor.execute('SELECT * FROM api_keys ORDER BY created_at DESC')
            
            results = cursor.fetchall()
            conn.close()
            
            # Remove hashes
            keys_list = []
            for row in results:
                d = dict(row)
                d.pop('key_hash', None)
                keys_list.append(d)
            
            return keys_list
        except Exception as e:
            print(f"❌ Error getting keys: {e}")
            return []
    
    def revoke_key(self, key_id: str) -> Dict:
        """
        Revoke API key
        
        Args:
            key_id: Key to revoke
        
        Returns:
            Status dict
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE api_keys SET is_active = 0 WHERE key_id = ?
            ''', (key_id,))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Key {key_id} revoked",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def register_device(self, device_id: str, device_name: str, 
                       device_type: str, api_key_id: str, ip_address: str = "") -> Dict:
        """
        Register connected device
        
        Args:
            device_id: Unique device ID
            device_name: Device name
            device_type: Type (pc, dashboard, agent, etc.)
            api_key_id: Associated API key
            ip_address: Device IP
        
        Returns:
            Status dict
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO connected_devices 
                (device_id, device_name, device_type, api_key_id, ip_address, status, last_seen)
                VALUES (?, ?, ?, ?, ?, 'online', ?)
            ''', (device_id, device_name, device_type, api_key_id, ip_address, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "device_id": device_id,
                "message": f"Device {device_name} registered",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_connected_devices(self) -> List[Dict]:
        """
        Get all connected devices
        
        Returns:
            List of devices
        """
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM connected_devices 
                WHERE status = 'online'
                ORDER BY last_seen DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Error getting devices: {e}")
            return []
    
    def log_access(self, key_id: str, endpoint: str, method: str, 
                  status: int, ip_address: str = "") -> bool:
        """
        Log API access
        
        Args:
            key_id: API key used
            endpoint: Endpoint accessed
            method: HTTP method
            status: Response status
            ip_address: Client IP
        
        Returns:
            Success bool
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs (key_id, endpoint, method, status, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (key_id, endpoint, method, status, ip_address))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error logging access: {e}")
            return False
    
    def get_access_logs(self, key_id: str = None, limit: int = 50) -> List[Dict]:
        """
        Get access logs
        
        Args:
            key_id: Filter by key (optional)
            limit: Max results
        
        Returns:
            List of logs
        """
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if key_id:
                cursor.execute('''
                    SELECT * FROM access_logs
                    WHERE key_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (key_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM access_logs
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Error getting logs: {e}")
            return []

# ============ SINGLETON ============
_auth_instance = None

def get_auth() -> AuthSystem:
    """Get or create Auth instance"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = AuthSystem()
    return _auth_instance
