# StreamAI Recording App

A Python application that integrates with OBS Studio and YouTube API to provide core functionality for recording sessions from your computer. This app can capture both video and audio from OBS and interact with YouTube's streaming platform.

## Features

- **OBS Integration**: Connect to OBS Studio via WebSocket API
- **YouTube API Integration**: Search videos, get channel info, and access live streams
- **Recording Management**: Start/stop recording sessions with automatic file organization
- **Session Management**: Create organized recording sessions with metadata
- **Real-time Status**: Monitor OBS recording and streaming status
- **Audio Source Detection**: Automatically detect and list audio sources from OBS
- **Web Frontend**: Modern React-based web interface for easy control
- **Real-time Transcription**: Live audio transcription using OpenAI Whisper
- **AI Text Refinement**: Improve transcriptions using LLaMA model via Groq API
- **Communication Bubbles**: Chat-like interface showing conversation between raw and refined text
- **Flask API**: RESTful API backend with WebSocket support

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
   
   # Groq API Configuration (for AI transcription refinement)
   GROQ_API_KEY=your_groq_api_key_here
   
   # OBS WebSocket Configuration
   OBS_HOST=localhost
   OBS_PORT=4455
   OBS_PASSWORD=your_obs_websocket_password
   
   # Recording Configuration
   RECORDINGS_PATH=./recordings
   LOG_LEVEL=INFO
   
   # API Server Configuration
   FLASK_HOST=localhost
   FLASK_PORT=5001
   FLASK_DEBUG=False
   ```

4. **Configure OBS WebSocket**:
   - Open OBS Studio
   - Go to Tools → WebSocket Server Settings
   - Enable WebSocket server
   - Set port (default: 4455)
   - Set password (use the same in your .env file)

## Usage

The application provides both a command-line interface and a web-based frontend with Flask API backend. For the complete real-time transcription experience, you'll want to use the web frontend.

### Quick Start: Real-time Transcription

To get the complete real-time transcription experience working:

**Step 1: Start the Backend API**
```bash
cd obs
python api_server.py
```
Keep this terminal open - the API server must run continuously.

**Step 2: Start Real-time Transcription Service**
```bash
# In a new terminal
cd realtime_audio
pip install -r requirements.txt  # first time only
python realtime_transcription_service.py
```
Keep this terminal open - it connects your microphone to the API.

**Step 3: Start the Frontend**
```bash
# In a third terminal
cd frontend
npm install  # first time only
npm run dev
```

**Step 4: Use the Web Interface**
1. Open `http://localhost:5173` in your browser
2. Click the "Transcription" tab
3. Click "Start Listening" 
4. Speak into your microphone
5. Watch real-time transcriptions appear as blue chat bubbles
6. Click "Stop Listening" when done

### Running the Backend API Server

Before using the web frontend, you need to start the Flask API server:

```bash
# Navigate to the obs directory
cd obs

# Start the Flask API server
python api_server.py
```

The API server will start on `http://localhost:5001` by default and provides:
- REST API endpoints for frontend communication
- WebSocket support for real-time updates
- Transcription management endpoints
- OBS integration endpoints
- YouTube API integration

**API Server Features:**
- `/api/status` - Get system status
- `/api/recording/start` - Start recording
- `/api/recording/stop` - Stop recording
- `/api/recordings` - List all recordings
- `/api/transcription/prompt` - Manage refinement prompts
- `/api/transcription/poll` - Poll for new transcriptions
- `/api/transcription/refine` - Refine transcriptions using AI

### Running the Frontend

After starting the backend API server, you can run the frontend:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port shown in the terminal).

### Command-Line Interface

The application also provides a command-line interface with several commands:

### Basic Commands

**Check system status**:
```bash
python main.py status
```

**Run system tests**:
```bash
python main.py test
```

**Test transcription system**:
```bash
# Make sure API server is running first
python test_transcription_system.py
```

**Set up and use real-time transcription** (connects your voice to frontend blue bubbles):
```bash
# 1. Install realtime audio dependencies
cd realtime_audio
pip install -r requirements.txt
cd ..

# 2. Start the Flask API server (required for frontend integration)
cd obs
python api_server.py
# Keep this running in one terminal

# 3. Start the real-time transcription service (in another terminal)
cd realtime_audio
python realtime_transcription_service.py
# This connects audio capture to the API server

# 4. Start the frontend (in a third terminal)
cd frontend
npm install  # first time only
npm run dev
# Open http://localhost:5173 and go to Transcription tab
# Click "Start Listening" to see real-time transcriptions
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

## Real-time Audio Transcription Setup

The StreamAI app includes a powerful real-time transcription feature that captures your voice and displays transcriptions as blue chat bubbles in the web interface.

### Prerequisites for Real-time Transcription

1. **Microphone access** - Ensure your microphone is working and accessible to Python
2. **API server running** - The Flask API server must be running for frontend integration
3. **Frontend running** - The React frontend must be running to see transcriptions

### Installation Steps

1. **Install realtime_audio dependencies**:
   ```bash
   cd realtime_audio
   pip install -r requirements.txt
   ```

   This installs:
   - `openai-whisper` - For speech-to-text transcription
   - `sounddevice` - For audio capture from microphone
   - `numpy` - For audio data processing
   - `requests` - For API communication
   - `python-dotenv` - For environment variable management
   - `groq` - For AI text refinement (optional)

2. **Set up environment variables** (optional for AI refinement):
   ```bash
   # In your .env file (create if it doesn't exist)
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Running Real-time Transcription

#### Method 1: Full Web Integration (Recommended)

This method provides the complete experience with blue chat bubbles in the web interface:

```bash
# Terminal 1: Start the Flask API server
cd obs
python api_server.py
# Leave this running

# Terminal 2: Start the real-time transcription service
cd realtime_audio
python realtime_transcription_service.py
# Leave this running

# Terminal 3: Start the frontend
cd frontend
npm install  # first time only
npm run dev
# Open http://localhost:5173
```

**Usage**:
1. Open the web interface at `http://localhost:5173`
2. Click on the "Transcription" tab
3. Click "Start Listening" button
4. Speak into your microphone
5. See real-time transcriptions appear as blue bubbles
6. Click "Stop Listening" when done

#### Method 2: Console Mode (Standalone)

For command-line usage without the web interface:

```bash
cd realtime_audio
python main.py
```

This runs a console-based version that:
- Captures audio from your microphone
- Shows raw transcriptions in the terminal
- Optionally refines text using AI (if Groq API key is configured)

### Troubleshooting Real-time Transcription

**Audio capture issues**:
```bash
# Test microphone access
python -c "import sounddevice; print(sounddevice.query_devices())"
# This should list your audio devices
```

**Whisper model download**:
- First run may take time to download the Whisper model
- Requires internet connection for initial setup
- Models are cached locally after first download

**API connection issues**:
- Ensure Flask API server is running on port 5001
- Check that no firewall is blocking localhost connections
- Verify the API server shows "Real-time Transcription Service initialized"

**Performance optimization**:
- Use `base` Whisper model for faster processing (default)
- Upgrade to `small` or `medium` models for better accuracy if needed
- Close other audio applications to reduce conflicts

### Real-time Transcription Architecture

The system works in three connected parts:

1. **Audio Capture** (`audio_capture.py`) - Captures microphone input
2. **Transcription** (`transcription.py`) - Processes audio with Whisper
3. **API Integration** (`realtime_transcription_service.py`) - Sends results to frontend

Data flows: `Microphone → Audio Capture → Whisper → API Server → Frontend Chat Bubbles`

```
streamAI/
├── obs/                           # Backend Python application
│   ├── main.py                   # Main CLI application entry point
│   ├── api_server.py            # Flask API server for frontend
│   ├── config.py                # Configuration management
│   ├── obs_controller.py        # OBS WebSocket API integration
│   ├── youtube_api.py           # YouTube API integration
│   ├── recording_manager.py     # Main recording coordination logic
│   ├── stream_analytics.py      # Performance analytics
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example            # Environment variables template
│   ├── .env                    # Your environment variables (create this)
│   └── recordings/             # Default recordings directory (auto-created)
├── frontend/                      # React TypeScript frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Dashboard.tsx    # Main dashboard
│   │   │   ├── Transcription.tsx # Real-time transcription chat
│   │   │   ├── Recordings.tsx   # Recording management
│   │   │   ├── Settings.tsx     # Application settings
│   │   │   └── ...             # Other components
│   │   ├── App.tsx             # Main App component
│   │   └── main.tsx            # React entry point
│   ├── package.json            # Frontend dependencies
│   └── vite.config.ts          # Vite configuration
├── realtime_audio/               # Real-time transcription system
│   ├── requirements.txt         # Audio processing dependencies
│   ├── realtime_transcription_service.py # Main service for web integration
│   ├── main.py                 # Console-based transcription mode
│   ├── transcription.py         # Whisper integration
│   ├── refinement.py           # LLaMA/Groq AI refinement
│   ├── audio_capture.py        # Audio capture functionality
│   └── console_ui.py           # Console user interface
├── test_transcription_system.py  # Integration test script
├── test_api_transcription.py     # API transcription tests
└── README.md                    # This file
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

**Real-time Transcription Issues**:
- **Microphone not detected**: Run `python -c "import sounddevice; print(sounddevice.query_devices())"` to list audio devices
- **Import errors**: Ensure you installed dependencies: `cd realtime_audio && pip install -r requirements.txt`
- **Whisper model download fails**: Check internet connection - first run downloads the model
- **No transcriptions appearing**: 
  - Verify API server is running on port 5001
  - Check that realtime_transcription_service.py shows "Started listening for audio"
  - Ensure frontend is connected and "Start Listening" was clicked
- **Audio quality issues**: Try speaking closer to the microphone or reducing background noise
- **Slow transcription**: Use `base` Whisper model (default) for faster processing

**Frontend Connection Issues**:
- Check that API server shows "Real-time Transcription Service initialized" on startup
- Verify frontend can reach `http://localhost:5001/api/health`
- Clear browser cache if transcription UI doesn't update

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

### Backend Python Dependencies (obs/)
- `obs-websocket-py`: OBS WebSocket client
- `google-api-python-client`: YouTube API client
- `python-dotenv`: Environment variable management
- `flask`: Web framework for API server
- `flask-cors`: CORS support for frontend communication
- `flask-socketio`: WebSocket support for real-time updates
- `groq`: Groq API client for AI text refinement
- Standard Python libraries (asyncio, logging, pathlib, etc.)

### Real-time Audio Dependencies (realtime_audio/)
- `openai-whisper`: OpenAI Whisper for speech-to-text transcription
- `sounddevice`: Audio capture from microphone
- `numpy`: Numerical computing for audio processing
- `requests`: HTTP client for API communication
- `python-dotenv`: Environment variable management
- `groq`: Groq API client for AI text refinement (optional)

### Frontend Dependencies
- `react`: React framework
- `typescript`: TypeScript support
- `vite`: Build tool and development server
- `tailwindcss`: CSS framework for styling
- `lucide-react`: Icon library
- Other React ecosystem packages

## License

This project is provided as-is for educational and development purposes.
