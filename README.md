# StreamAI Recording App

A Python application that integrates with OBS Studio and YouTube API to provide core functionality for recording sessions from your computer. This app can capture both video and audio from OBS and interact with YouTube's streaming platform.

## Features

- **OBS Integration**: Connect to OBS Studio via WebSocket API
- **YouTube API Integration**: Search videos, get channel info, and access live streams
- **Recording Management**: Start/stop recording sessions with automatic file organization
- **Session Management**: Create organized recording sessions with metadata
- **Real-time Status**: Monitor OBS recording and streaming status
- **Audio Source Detection**: Automatically detect and list audio sources from OBS

## Prerequisites

### Required Software
1. **OBS Studio** with **obs-websocket plugin** installed
   - Download OBS: https://obsproject.com/
   - Install obs-websocket plugin (usually included in recent OBS versions)
   - Enable WebSocket server in OBS: Tools → WebSocket Server Settings

2. **Python 3.8+**

### API Keys
- **YouTube Data API v3 Key** (optional, for YouTube features)
  - Get from Google Cloud Console: https://console.cloud.google.com/
  - Enable YouTube Data API v3
  - Create credentials (API Key)

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   cd obs
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your settings:
   ```env
   # YouTube API Configuration
   YOUTUBE_API_KEY=your_youtube_api_key_here
   
   # OBS WebSocket Configuration
   OBS_HOST=localhost
   OBS_PORT=4455
   OBS_PASSWORD=your_obs_websocket_password
   
   # Recording Configuration
   RECORDINGS_PATH=./recordings
   LOG_LEVEL=INFO
   ```

4. **Configure OBS WebSocket**:
   - Open OBS Studio
   - Go to Tools → WebSocket Server Settings
   - Enable WebSocket server
   - Set port (default: 4455)
   - Set password (use the same in your .env file)

## Usage

The application provides a command-line interface with several commands:

### Basic Commands

**Check system status**:
```bash
python main.py status
```

**Run system tests**:
```bash
python main.py test
```

**Start recording session (quick start/stop)**:
```bash
python main.py start
# or with custom session name
python main.py start --session-name "my_recording_session"
```

**Start continuous recording session** (recommended):
```bash
python main.py record
# or with custom session name
python main.py record --session-name "my_live_session"
```

**Stop recording session**:
```bash
python main.py stop
```

**List all recording sessions**:
```bash
python main.py list
```

### Recording Modes

The app supports two recording modes:

1. **Quick Mode** (`start` command):
   - Starts recording and immediately exits
   - Use for automated scripts or quick recordings
   - Must use `stop` command to end recording

2. **Continuous Mode** (`record` command) - **RECOMMENDED**:
   - Starts recording and keeps running with real-time monitoring
   - Shows live recording status every 10 seconds
   - Press `Ctrl+C` to stop recording gracefully
   - Can also use `python main.py stop` in another terminal

**Example continuous recording session**:
```bash
# Terminal 1: Start continuous recording
python main.py record --session-name "my_stream"

# Output:
# ✅ Recording session started: my_stream
# 🔴 RECORDING IN PROGRESS
# Press Ctrl+C to stop recording or use 'python main.py stop' in another terminal
# 📹 Recording: 00:01:30 | Size: 45.2 MB
# 🔴 Streaming: 00:01:30 | Frames: 2,700 | Dropped: 0

# Terminal 2 (optional): Stop from another terminal
python main.py stop
```

### Data Retrieval Commands

**Get current OBS data** (scenes, recording status, audio sources):
```bash
python main.py obs-data
```

**Get YouTube data**:
```bash
# Search for videos
python main.py youtube --query "python tutorial"

# Get channel information
python main.py youtube --channel-id "UC_channel_id_here"

# Get live streams
python main.py youtube
```

## Project Structure

```
obs/
├── main.py                 # Main application entry point
├── config.py              # Configuration management
├── obs_controller.py      # OBS WebSocket API integration
├── youtube_api.py         # YouTube API integration
├── recording_manager.py   # Main recording coordination logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (create this)
├── recordings/           # Default recordings directory (auto-created)
└── README.md            # This file
```

## Core Functionality

### OBS Integration
- Connect to OBS via WebSocket
- Start/stop recordings
- Get current scene information
- Monitor recording and streaming status
- Detect audio sources
- Retrieve recording folder path

### YouTube API Integration
- Search for videos
- Get channel information and statistics
- Find live streams
- API quota management
- Error handling for API limits

### Recording Management
- Create organized recording sessions
- Automatic file organization
- Session metadata tracking
- Copy recordings to session folders
- JSON metadata export

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | None |
| `OBS_HOST` | OBS WebSocket host | localhost |
| `OBS_PORT` | OBS WebSocket port | 4455 |
| `OBS_PASSWORD` | OBS WebSocket password | None |
| `RECORDINGS_PATH` | Local recordings directory | ./recordings |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |

## Development & Debugging

### Python Debugger Setup

For developers who want to debug the application, you can use Python's built-in debugger or IDE debugging features.

#### Using Python Debugger (pdb)

**Add breakpoints in code**:
```python
import pdb; pdb.set_trace()
```

**Run with debugger**:
```bash
python -m pdb main.py record --session-name "debug_session"
```

**Common pdb commands**:
- `n` (next line)
- `s` (step into function)
- `c` (continue)
- `l` (list current code)
- `p variable_name` (print variable)
- `q` (quit debugger)

#### Using VS Code Debugger

Create `.vscode/launch.json` for VS Code debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "StreamAI: Record Session",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/obs/main.py",
            "args": ["record", "--session-name", "debug_session"],
            "cwd": "${workspaceFolder}/obs",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/obs/.env"
        },
        {
            "name": "StreamAI: Status Check",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/obs/main.py",
            "args": ["status"],
            "cwd": "${workspaceFolder}/obs",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/obs/.env"
        },
        {
            "name": "StreamAI: Run Tests",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/obs/main.py",
            "args": ["test"],
            "cwd": "${workspaceFolder}/obs",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/obs/.env"
        },
        {
            "name": "StreamAI: Analytics",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/obs/stream_analytics.py",
            "cwd": "${workspaceFolder}/obs",
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/obs/.env"
        }
    ]
}
```

#### Debug Mode Environment

Set debug logging in your `.env` file:
```env
LOG_LEVEL=DEBUG
```

This will provide detailed logging information for troubleshooting.

### Advanced Analytics

**Run detailed stream analytics**:
```bash
cd obs
python stream_analytics.py
```

This provides comprehensive analysis including:
- Performance metrics (FPS, frame drops)
- Stream quality analysis
- Audio configuration review
- Network quality assessment
- Optimization recommendations

## Troubleshooting

### Common Issues

**OBS Connection Failed**:
- Ensure OBS is running
- Check WebSocket server is enabled in OBS
- Verify host, port, and password in .env file
- Check firewall settings

**YouTube API Errors**:
- Verify API key is correct
- Check API quotas in Google Cloud Console
- Ensure YouTube Data API v3 is enabled

**Recording Not Starting**:
- Check OBS recording settings
- Ensure sufficient disk space
- Verify recording path permissions

**Continuous Recording Stops Immediately**:
- Check if OBS is actually recording (not just streaming)
- Verify recording path is writable
- Check OBS recording settings and output format

### Logs

Application logs are saved to `recording_app.log` in the same directory. Check this file for detailed error information.

**Enable debug logging**:
```bash
# Set in .env file
LOG_LEVEL=DEBUG

# Then run any command to see detailed logs
python main.py status
```

## Example Workflow

1. **Setup and test**:
   ```bash
   python main.py test
   ```

2. **Check status**:
   ```bash
   python main.py status
   ```

3. **Start recording**:
   ```bash
   python main.py start --session-name "my_stream_session"
   ```

4. **Monitor** (in another terminal):
   ```bash
   python main.py obs-data
   ```

5. **Stop recording**:
   ```bash
   python main.py stop
   ```

6. **Review sessions**:
   ```bash
   python main.py list
   ```

## Future Enhancements

This core functionality can be extended with:
- Web interface for remote control
- Server-based storage integration
- Real-time streaming to platforms
- Advanced recording scheduling
- Multi-camera support
- Automated post-processing

## Dependencies

- `obs-websocket-py`: OBS WebSocket client
- `google-api-python-client`: YouTube API client
- `python-dotenv`: Environment variable management
- Standard Python libraries (asyncio, logging, pathlib, etc.)

## License

This project is provided as-is for educational and development purposes.
