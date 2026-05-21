# 🤖 JARVIS AI Control System

**Iron Man Style AI Assistant** - Vollständiges System zur Kontrolle und zum Training einer KI mit Web-Interface und 24/7 Backend.

## 🎯 Features

- ✅ **Echtzeit Control Panel** - Dashboard für KI-Steuerung
- ✅ **Chat Interface** - Kommunikation mit JARVIS
- ✅ **Background AI Training** - KI trainiert sich selbst
- ✅ **3D Hologram Avatar** - Iron Man Style Visualisierung
- ✅ **SQLite Datenbank** - Speichert alle Daten
- ✅ **REST API** - Alle Funktionen via API
- ✅ **24/7 Hosting** - Kostenlos auf Render.com
- ✅ **Full History** - Chat, Training, Activity Logs

## 📁 Projektstruktur

```
jarvis-ai-system/
├── backend/
│   ├── app.py              # FastAPI Server
│   ├── config.py           # Konfiguration
│   ├── database.py         # Datenbankfunktionen
│   ├── ai_worker.py        # Background AI Thread
│   └── api_routes.py       # API Endpoints
├── frontend/
│   ├── index.html          # Chat Interface
│   ├── dashboard.html      # Control Panel
│   └── assets/
│       └── style.css       # Styling
├── data/
│   └── jarvis_database.db  # SQLite Database
├── requirements.txt        # Python Dependencies
├── .env                    # Umgebungsvariablen
├── .gitignore             # Git Ignore
├── render.yaml            # Render.com Config
└── README.md              # Diese Datei
```

## 🚀 Quick Start (Lokal)

### 1. Repository clonen
```bash
git clone https://github.com/felixdegro25-blip/jarvis-ai-system.git
cd jarvis-ai-system
```

### 2. Virtual Environment erstellen
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Backend starten
```bash
python -m backend.app
```

Backend läuft auf: **http://localhost:5000**

### 5. Frontend öffnen
- Chat: Öffne `frontend/index.html` im Browser
- Dashboard: Öffne `frontend/dashboard.html` im Browser

## ☁️ Deployment auf Render.com (24/7 Kostenlos)

### 1. Render.com Account erstellen
- Gehe zu [render.com](https://render.com)
- Melde dich mit GitHub an

### 2. New Web Service erstellen
- Klick "Create" → "Web Service"
- GitHub Repo `jarvis-ai-system` wählen
- Name: `jarvis-ai-system`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
- Plan: **Free** ✅
- Deploy! 🚀

### 3. URL verwenden
Dein Server läuft unter:
```
https://jarvis-ai-system.onrender.com
```

Aktualisiere `frontend/index.html` und `frontend/dashboard.html`:
```javascript
const API_BASE = 'https://jarvis-ai-system.onrender.com/api';
```

## 📡 API Endpoints

### Status
```
GET /api/status
```
Response:
```json
{
  "status": "online",
  "cpu": 45.2,
  "memory": 62.1,
  "gpu": 38.5,
  "temp": 42.3,
  "uptime": 3600
}
```

### Activity
```
GET /api/activity
```
Response:
```json
{
  "current_task": "Processing request",
  "processing_time": 125,
  "confidence": 92.5,
  "input": "Hello JARVIS",
  "output": "Response from JARVIS"
}
```

### Training
```
GET /api/training
```
Response:
```json
{
  "progress": 45,
  "epochs": 45,
  "accuracy": 87.5,
  "loss": 0.215,
  "is_training": true
}
```

### Control Commands
```
POST /api/control/start
POST /api/control/pause
POST /api/control/shutdown
POST /api/control/training (body: {"mode": "intensive"})
POST /api/control/command (body: {"command": "text"})
```

### History
```
GET /api/history/chat?limit=10
GET /api/history/training?limit=20
GET /api/history/activity?limit=20
```

## 🧠 KI Integration

### Deine AI Module verbinden

Du kannst deine JARVIS Module über die API verbinden:

```python
import requests

# Backend API URL
API_URL = "http://localhost:5000/api"

# Sende Befehl an JARVIS
def send_command(text):
    response = requests.post(
        f"{API_URL}/control/command",
        json={"command": text}
    )
    return response.json()

# Starte Training
def start_training():
    response = requests.post(
        f"{API_URL}/control/training",
        json={"mode": "intensive"}
    )
    return response.json()

# Hole aktuelle Status
def get_status():
    response = requests.get(f"{API_URL}/status")
    return response.json()
```

## 🔧 Konfiguration

Bearbeite `.env`:
```
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DATABASE_PATH=data/jarvis_database.db
DEBUG=True
API_TIMEOUT=30
```

## 📊 Datenbank Schema

### system_status
```sql
id, status, cpu, memory, gpu, temperature, uptime, timestamp
```

### activity_log
```sql
id, task, processing_time, confidence, input_text, output_text, timestamp
```

### training_data
```sql
id, epoch, accuracy, loss, progress, is_training, mode, timestamp
```

### chat_history
```sql
id, user_message, ai_response, confidence, timestamp
```

### ai_models
```sql
id, model_name, model_data, accuracy, parameters, created_at, updated_at
```

## 🎨 Frontend Anpassung

### Chat Interface (`frontend/index.html`)
- Ändere API URL in der Datei
- Passe Styling nach Belieben an
- Integriere deine JARVIS Module

### Control Dashboard (`frontend/dashboard.html`)
- 3D Würfel Visualisierung
- Real-time Metriken
- Training Controls
- System Logs

## 🐛 Troubleshooting

### Backend startet nicht
```bash
pip install --upgrade fastapi uvicorn
python -m backend.app
```

### Datenbank-Fehler
```bash
rm data/jarvis_database.db  # Löschen
python -m backend.app       # Neu erstellen
```

### CORS Fehler
- Backend hat CORS aktiviert ✅
- Frontend URL muss korrekt sein

## 📝 Environment Variables

```bash
SERVER_HOST=0.0.0.0          # Server Host
SERVER_PORT=5000             # Server Port
DATABASE_PATH=data/jarvis_database.db
DEBUG=True                    # Debug Mode
API_TIMEOUT=30               # API Timeout (Sekunden)
```

## 🚀 Performance Tipps

1. **Datenbank optimieren**: Regelmäßig alte Logs löschen
2. **Background Worker**: Läuft in separatem Thread
3. **Caching**: Nutze Redis für schnellere Responses
4. **CDN**: Für Frontend Assets verwenden

## 📞 Support

- 🐛 Bugs: GitHub Issues erstellen
- 💬 Fragen: GitHub Discussions
- 📧 Email: deine@email.com

## 📄 Lizenz

MIT License - Frei nutzbar!

## 👨‍💻 Autor

felixdegro25-blip

---

**Made with ❤️ for JARVIS**
