"""\n🚀 JARVIS Dashboard Setup & API Configuration Generator
Kreiert API Keys und konfiguriert dein PC Dashboard
"""

import os
import sys
import json
import socket
from datetime import datetime

def get_local_ip():
    """Get local machine IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_config():
    """
    Generate JARVIS configuration
    """
    print("\n" + "="*60)
    print(" 🚀 JARVIS Dashboard Setup & Configuration")
    print("="*60 + "\n")
    
    local_ip = get_local_ip()
    
    print("🔗 Network Information:")
    print(f"   Local IP: {local_ip}")
    print(f"   Localhost: 127.0.0.1")
    print()
    
    # Get configuration inputs
    print("🎮 Configuration Setup:\n")
    
    api_key_name = input("API Key Name (z.B. 'PC Dashboard'): ").strip() or "PC Dashboard"
    
    pc_server_url = input(f"PC Server URL (Enter for localhost:8765): ").strip() or "http://localhost:8765"
    
    pc_api_key = input("PC Server API Key (Enter for default): ").strip() or "DEIN_GEHEIMER_API_KEY"
    
    use_remote = input("\nSoll JARVIS Server lokal (http://{local_ip}:5000) oder remote laufen? (local/remote): ").strip().lower() or "local"
    
    if use_remote == "remote":
        jarvis_server = input("Remote JARVIS Server URL (z.B. https://jarvis-ai-system.onrender.com): ").strip()
    else:
        jarvis_server = f"http://{local_ip}:5000"
    
    # Generate configuration
    config = {
        "timestamp": datetime.now().isoformat(),
        "jarvis_server": jarvis_server,
        "pc_server": {
            "url": pc_server_url,
            "api_key": pc_api_key
        },
        "api_key_name": api_key_name,
        "local_ip": local_ip,
        "platform": sys.platform
    }
    
    # Display configuration
    print("\n" + "="*60)
    print("✅ Configuration Generated:")
    print("="*60)
    print(json.dumps(config, indent=2))
    print("="*60 + "\n")
    
    # Save to file
    config_file = "jarvis_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📄 Configuration saved to: {config_file}\n")
    
    # Generate dashboard HTML configuration
    dashboard_config = f"""
<!-- JARVIS Dashboard Configuration -->
<script>
const JARVIS_CONFIG = {{
    API_BASE: '{jarvis_server}/api',
    PC_SERVER_URL: '{pc_server_url}',
    PC_API_KEY: '{pc_api_key}',
    UPDATE_INTERVAL: 2000,
    AUTOSTART: true
}};
</script>
    """
    
    print("📊 Dashboard Configuration Script:")
    print("")
    print(dashboard_config)
    print()
    
    # Save dashboard config
    config_js_file = "dashboard_config.js"
    with open(config_js_file, 'w') as f:
        f.write(dashboard_config)
    
    print(f"📄 Dashboard config saved to: {config_js_file}\n")
    
    print("="*60)
    print("👏 Setup Complete!")
    print("="*60)
    print("✅ Configuration saved")
    print("✅ Ready to use with JARVIS Dashboard")
    print(f"🌐 Access: {jarvis_server}")
    print("="*60 + "\n")
    
    return config

if __name__ == "__main__":
    config = generate_config()
    print("🚀 Configuration ready for JARVIS!\n")
