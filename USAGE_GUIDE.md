# StreamAI Quick Usage Guide

## 🚀 Quick Start

### 1. Setup (One-time)
```bash
cd obs
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OBS WebSocket password
```

### 2. Test Everything Works
```bash
python main.py test
```

### 3. Start Recording (Continuous Mode - RECOMMENDED)
```bash
python main.py record --session-name "my_session"
```

**This will:**
- ✅ Start OBS recording
- ✅ Keep running with live status updates
- ✅ Show recording time, file size, and stream stats
- ✅ Press `Ctrl+C` to stop gracefully

### 4. Stop Recording (Alternative)
```bash
# In another terminal (optional)
python main.py stop
```

## 📊 Key Features

### Recording Modes
- **`record`** - Continuous recording with live monitoring (RECOMMENDED)
- **`start`** - Quick start and exit (for scripts)

### Data Analysis
```bash
python stream_analytics.py  # Detailed performance analysis
python main.py obs-data     # Raw OBS data
python main.py status       # System status
```

### Session Management
```bash
python main.py list         # List all recordings
```

## 🔧 VS Code Debugging

1. Open project in VS Code
2. Go to Run & Debug (Ctrl+Shift+D)
3. Select "StreamAI: Record Session" 
4. Press F5 to start debugging

## 📁 File Organization

```
recordings/
├── my_session_20250706_165000/
│   ├── 2025-07-06 16-50-00.mkv    # Your recording
│   └── session_metadata.json      # Session info
└── another_session_20250706_170000/
    └── ...
```

## 🎯 What You Get

- **Real-time monitoring**: See recording progress live
- **Automatic file organization**: Each session in its own folder
- **Performance analytics**: FPS, frame drops, bitrate analysis
- **Audio source detection**: Monitor all audio inputs
- **Session metadata**: JSON export of all session data

## 🐛 Troubleshooting

**Recording stops immediately?**
- Make sure OBS is running and recording (not just streaming)
- Check OBS WebSocket is enabled (Tools → WebSocket Server Settings)

**Can't connect to OBS?**
- Verify OBS WebSocket password in `.env` file
- Check OBS is running on localhost:4455

**Need debug info?**
```bash
# Set LOG_LEVEL=DEBUG in .env file
python main.py status  # Will show detailed logs
```

## 💡 Pro Tips

1. **Use continuous mode**: `python main.py record` gives you real-time feedback
2. **Monitor in real-time**: Watch for frame drops and performance issues
3. **Check analytics**: Run `python stream_analytics.py` for detailed insights
4. **Organize sessions**: Use meaningful session names with `--session-name`
5. **Debug easily**: Use VS Code debugger configurations for development

---

**Need help?** Check the full README.md for complete documentation!
