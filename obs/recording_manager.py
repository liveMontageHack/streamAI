import asyncio
import logging
import shutil
from datetime import datetime
from pathlib import Path
from obs_controller import OBSController
from youtube_api import YouTubeAPI
from config import config

class RecordingManager:
    """Main recording manager that coordinates OBS and YouTube API functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.obs_controller = OBSController()
        self.youtube_api = YouTubeAPI()
        self.current_session = None
        self.recordings_path = config.get_recordings_path()
        
    async def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing Recording Manager...")
        
        # Connect to OBS
        obs_connected = await self.obs_controller.connect()
        if not obs_connected:
            self.logger.error("Failed to connect to OBS. Recording functionality will be limited.")
            return False
        
        # Validate YouTube API
        if self.youtube_api.is_authenticated():
            api_valid = self.youtube_api.validate_api_key()
            if not api_valid:
                self.logger.warning("YouTube API validation failed. YouTube features will be limited.")
        
        self.logger.info("Recording Manager initialized successfully")
        return True
    
    def get_system_status(self):
        """Get overall system status"""
        status = {
            'obs_connected': self.obs_controller.is_connected(),
            'youtube_authenticated': self.youtube_api.is_authenticated(),
            'recordings_path': str(self.recordings_path),
            'current_session': self.current_session,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.obs_controller.is_connected():
            status['obs_version'] = self.obs_controller.get_version_info()
            status['current_scene'] = self.obs_controller.get_current_scene()
            status['recording_status'] = self.obs_controller.get_recording_status()
            status['stream_status'] = self.obs_controller.get_stream_status()
            status['audio_sources'] = self.obs_controller.get_audio_sources()
        
        return status
    
    def create_session(self, session_name=None):
        """Create a new recording session"""
        if not session_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"recording_session_{timestamp}"
        
        session_path = self.recordings_path / session_name
        session_path.mkdir(parents=True, exist_ok=True)
        
        self.current_session = {
            'name': session_name,
            'path': session_path,
            'start_time': datetime.now(),
            'status': 'created',
            'obs_recordings': [],
            'metadata': {}
        }
        
        self.logger.info(f"Created new session: {session_name}")
        return self.current_session
    
    async def start_recording_session(self, session_name=None):
        """Start a complete recording session"""
        if not self.obs_controller.is_connected():
            self.logger.error("Cannot start recording: OBS not connected")
            return False
        
        # Create session if not exists
        if not self.current_session:
            self.create_session(session_name)
        
        # Get current OBS status
        obs_status = self.obs_controller.get_recording_status()
        if obs_status and obs_status['active']:
            self.logger.warning("OBS recording already active")
            self.current_session['status'] = 'recording'
            return True
        
        # Start OBS recording
        recording_started = self.obs_controller.start_recording()
        if recording_started:
            self.current_session['status'] = 'recording'
            self.current_session['obs_start_time'] = datetime.now()
            
            # Get recording folder from OBS
            obs_folder = self.obs_controller.get_recording_folder()
            if obs_folder:
                self.current_session['obs_recording_folder'] = obs_folder
            
            self.logger.info(f"Recording session started: {self.current_session['name']}")
            return True
        else:
            self.logger.error("Failed to start OBS recording")
            return False
    
    async def stop_recording_session(self):
        """Stop the current recording session"""
        if not self.obs_controller.is_connected():
            self.logger.error("Cannot stop recording: OBS not connected")
            return False
        
        # Check if there's an active OBS recording first
        obs_status = self.obs_controller.get_recording_status()
        if not obs_status or not obs_status['active']:
            self.logger.warning("No active OBS recording to stop")
            
            # If we have a session, mark it as stopped anyway
            if self.current_session:
                self.current_session['status'] = 'stopped'
                self.current_session['end_time'] = datetime.now()
                self.logger.info(f"Session marked as stopped: {self.current_session['name']}")
                return True
            else:
                self.logger.warning("No active session to stop")
                return False
        
        # Stop OBS recording
        result = self.obs_controller.stop_recording()
        if result:
            # Update session if exists
            if self.current_session:
                self.current_session['status'] = 'stopped'
                self.current_session['end_time'] = datetime.now()
                
                # If result contains file path, save it
                if isinstance(result, str) and result != True:
                    self.current_session['obs_recordings'].append(result)
                    
                    # Copy recording to session folder
                    await self._copy_recording_to_session(result)
                
                self.logger.info(f"Recording session stopped: {self.current_session['name']}")
            else:
                self.logger.info("OBS recording stopped (no session was active)")
            
            return True
        else:
            self.logger.error("Failed to stop OBS recording")
            return False
    
    async def _copy_recording_to_session(self, obs_recording_path):
        """Copy OBS recording to session folder"""
        try:
            source_path = Path(obs_recording_path)
            if source_path.exists():
                dest_path = self.current_session['path'] / source_path.name
                shutil.copy2(source_path, dest_path)
                self.logger.info(f"Copied recording to session folder: {dest_path}")
                
                # Update session metadata
                self.current_session['local_recordings'] = self.current_session.get('local_recordings', [])
                self.current_session['local_recordings'].append(str(dest_path))
            else:
                self.logger.warning(f"OBS recording file not found: {obs_recording_path}")
        except Exception as e:
            self.logger.error(f"Failed to copy recording to session folder: {e}")
    
    def get_current_session_info(self):
        """Get information about the current session"""
        if not self.current_session:
            return None
        
        session_info = self.current_session.copy()
        
        # Add real-time OBS status if connected
        if self.obs_controller.is_connected():
            session_info['live_recording_status'] = self.obs_controller.get_recording_status()
            session_info['live_stream_status'] = self.obs_controller.get_stream_status()
        
        return session_info
    
    def list_sessions(self):
        """List all recording sessions"""
        sessions = []
        if self.recordings_path.exists():
            for session_dir in self.recordings_path.iterdir():
                if session_dir.is_dir():
                    session_info = {
                        'name': session_dir.name,
                        'path': str(session_dir),
                        'created': datetime.fromtimestamp(session_dir.stat().st_ctime),
                        'files': [f.name for f in session_dir.iterdir() if f.is_file()]
                    }
                    sessions.append(session_info)
        
        sessions.sort(key=lambda x: x['created'], reverse=True)
        return sessions
    
    def get_obs_data(self):
        """Get current OBS data (video and audio)"""
        if not self.obs_controller.is_connected():
            self.logger.error("Cannot get OBS data: not connected")
            return None
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'current_scene': self.obs_controller.get_current_scene(),
            'scenes_list': self.obs_controller.get_scenes_list(),
            'recording_status': self.obs_controller.get_recording_status(),
            'stream_status': self.obs_controller.get_stream_status(),
            'audio_sources': self.obs_controller.get_audio_sources(),
            'recording_folder': self.obs_controller.get_recording_folder()
        }
        
        return data
    
    def get_youtube_data(self, query=None, channel_id=None):
        """Get YouTube data"""
        if not self.youtube_api.is_authenticated():
            self.logger.error("Cannot get YouTube data: not authenticated")
            return None
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'authenticated': True
        }
        
        # Get channel info if channel_id provided
        if channel_id:
            data['channel_info'] = self.youtube_api.get_channel_info(channel_id)
        
        # Search videos if query provided
        if query:
            data['search_results'] = self.youtube_api.search_videos(query)
        
        # Get live streams
        data['live_streams'] = self.youtube_api.get_live_streams(channel_id)
        
        return data
    
    async def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up Recording Manager...")
        
        # Stop any active recording
        if self.current_session and self.current_session.get('status') == 'recording':
            await self.stop_recording_session()
        
        # Disconnect from OBS
        if self.obs_controller.is_connected():
            self.obs_controller.disconnect()
        
        self.logger.info("Recording Manager cleanup completed")
    
    def save_session_metadata(self, additional_metadata=None):
        """Save session metadata to file"""
        if not self.current_session:
            self.logger.warning("No current session to save metadata for")
            return False
        
        try:
            import json
            
            metadata = self.current_session.copy()
            
            # Convert datetime objects to strings for JSON serialization
            for key, value in metadata.items():
                if isinstance(value, datetime):
                    metadata[key] = value.isoformat()
            
            if additional_metadata:
                metadata['additional'] = additional_metadata
            
            metadata_file = self.current_session['path'] / 'session_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            self.logger.info(f"Session metadata saved to: {metadata_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save session metadata: {e}")
            return False
