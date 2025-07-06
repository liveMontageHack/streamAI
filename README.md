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

**Start recording session**:
```bash
python main.py start
# or with custom session name
python main.py start --session-name "my_recording_session"
```

**Stop recording session**:
```bash
python main.py stop
```

**List all recording sessions**:
```bash
python main.py list
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

### Logs

Application logs are saved to `recording_app.log` in the same directory. Check this file for detailed error information.

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
