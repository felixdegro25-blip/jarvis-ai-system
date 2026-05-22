# 🚀 JARVIS Complete Setup Guide

## Quick Start - 5 Minutes

### 1. Get Hugging Face API Key (FREE)

1. Go to [huggingface.co](https://huggingface.co)
2. Sign up (free)
3. Go to [Settings → Tokens](https://huggingface.co/settings/tokens)
4. Create new token → Copy it
5. Paste in `.env` file: `HF_API_KEY=your_key_here`

### 2. Local Setup

```bash
# Clone repo
git clone https://github.com/felixdegro25-blip/jarvis-ai-system.git
cd jarvis-ai-system

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start server
python -m backend.app
```

Server runs on: `http://localhost:5000`

### 3. Open Web Apps

- **Chat**: http://localhost:5000/static/index.html
- **Dashboard**: http://localhost:5000/static/dashboard.html
- **API Docs**: http://localhost:5000/docs

### 4. Start PC Agent (Your PC)

**Windows:**
```bash
cd pc_agent
java jarvis_pc_agent.bat
```

**Linux/Mac:**
```bash
cd pc_agent
chmod +x jarvis_pc_agent.sh
./jarvis_pc_agent.sh
```

---

## 📡 Production Deployment (Render.com)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Production ready"
git push origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com)
2. Click "New+" → "Web Service"
3. Select `jarvis-ai-system` repo
4. Fill settings:
   - **Name**: `jarvis-ai-system`
   - **Environment**: Python 3
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free ✅
5. Add environment variable:
   - **Key**: `HF_API_KEY`
   - **Value**: Your Hugging Face key
6. Click "Create Web Service"

### Step 3: Your Server URL

Wait 2-3 minutes, then access:
```
https://jarvis-ai-system.onrender.com
```

### Step 4: Update PC Agent

Edit `pc_agent/jarvis_pc_agent.py` line ~15:

```python
SERVER_URL = 'https://jarvis-ai-system.onrender.com'
```

Or set environment variable:
```bash
set JARVIS_SERVER_URL=https://jarvis-ai-system.onrender.com
```

---

## 🎮 API Usage Examples

### Chat with JARVIS

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather?"}'
```

### Create Task

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "due_date": "2024-06-01T18:00:00",
    "priority": 5
  }'
```

### PC Control - Shutdown

```bash
curl -X POST http://localhost:5000/api/pc/command \
  -H "Content-Type: application/json" \
  -d '{
    "action": "shutdown",
    "delay": 300
  }'
```

### Get Tasks

```bash
curl http://localhost:5000/api/tasks?status=pending
```

### Create Reminder

```bash
curl -X POST http://localhost:5000/api/reminders \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "reminder_time": "2024-06-01T17:00:00",
    "message": "Time to buy groceries!"
  }'
```

---

## 🔌 Integrate Your Own AI

Edit `backend/api_routes.py` → `execute_command()` function:

```python
@router.post("/api/control/command")
async def execute_command(cmd: ControlCommand):
    input_text = cmd.command
    
    # YOUR AI HERE:
    # output = your_ai_model(input_text)
    
    output_text = f"Processed: {cmd.command}"
    confidence = 85
    ...
```

---

## 📊 Database Tables

- **tasks**: To-do items, reminders, deadlines
- **reminders**: Time-based notifications
- **events**: Calendar events
- **chat_history**: All conversations
- **activity_log**: System actions
- **training_data**: AI learning progress
- **system_status**: PC metrics (CPU, Memory, etc.)

---

## 🔧 Configuration

### `.env` File

```bash
SERVER_HOST=0.0.0.0              # Server address
SERVER_PORT=5000                 # Server port
DATABASE_PATH=data/jarvis_database.db
DEBUG=True                        # Debug mode
HF_API_KEY=your_key_here         # Hugging Face API key
JARVIS_SERVER_URL=http://localhost:5000
JARVIS_API_KEY=jarvis-pc-agent-key
```

---

## 🐛 Troubleshooting

### "HF_API_KEY not set"

1. Get key from https://huggingface.co/settings/tokens
2. Add to `.env`: `HF_API_KEY=your_key`
3. Restart server

### "Model is loading"

First request to Hugging Face takes 1-2 minutes (model loads). Be patient!

### PC Agent won't connect

```bash
# Check server is running
curl http://localhost:5000/health

# Check PC Agent logs
python pc_agent/jarvis_pc_agent.py
```

### Port already in use

Change port in `.env`:
```bash
SERVER_PORT=8000  # Use different port
```

Or kill process:
```bash
# Windows
taskkill /PID <pid> /F

# Linux/Mac
kill -9 <pid>
```

---

## 🎯 Next Steps

1. ✅ Deploy on Render.com
2. ✅ Configure PC Agent on your PC
3. ✅ Create tasks and reminders
4. ✅ Chat with JARVIS AI
5. ✅ Test PC control (shutdown, restart, etc.)

---

## 📞 Support

- GitHub: [jarvis-ai-system](https://github.com/felixdegro25-blip/jarvis-ai-system)
- Hugging Face: https://huggingface.co
- Render: https://render.com

---

**Made with ❤️ for JARVIS**
