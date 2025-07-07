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
        self.logger.debug("Starting recording session...")
        
        if not self.obs_controller.is_connected():
            self.logger.error("Cannot start recording: OBS not connected")
            return False
        
        self.logger.debug("OBS is connected, proceeding...")
        
        # Create session if not exists
        if not self.current_session:
            self.logger.debug("Creating new session...")
            self.create_session(session_name)
        
        self.logger.debug("Checking current OBS recording status...")
        # Get current OBS status
        obs_status = self.obs_controller.get_recording_status()
        self.logger.debug(f"OBS status: {obs_status}")
        
        if obs_status and obs_status['active']:
            self.logger.warning("OBS recording already active")
            self.current_session['status'] = 'recording'
            return True
        
        self.logger.debug("Starting OBS recording...")
        # Start OBS recording
        recording_started = self.obs_controller.start_recording()
        self.logger.debug(f"Recording started result: {recording_started}")
        
        if recording_started:
            self.current_session['status'] = 'recording'
            self.current_session['obs_start_time'] = datetime.now()
            
            self.logger.debug("Getting recording folder from OBS...")
            # Get recording folder from OBS
            obs_folder = self.obs_controller.get_recording_folder()
            if obs_folder:
                self.current_session['obs_recording_folder'] = obs_folder
            
            # Save initial metadata
            self.save_session_metadata({'status': 'Recording in progress'})
            
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
                
                # Save metadata even if no recording was active
                self.save_session_metadata()
                
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
                
                # Wait a moment for OBS to finish writing the file
                import time
                time.sleep(1)
                
                # Find and copy the latest recording from OBS folder
                await self._find_and_copy_latest_recording()
                
                # Save metadata with all session information
                self.save_session_metadata()
                
                self.logger.info(f"Recording session stopped: {self.current_session['name']}")
            else:
                self.logger.info("OBS recording stopped (no session was active)")
            
            return True
        else:
            self.logger.error("Failed to stop OBS recording")
            return False
    
    async def _find_and_copy_latest_recording(self):
        """Find the latest recording in OBS folder and copy it to session folder"""
        try:
            # Get OBS recording folder
            obs_folder = self.current_session.get('obs_recording_folder')
            if not obs_folder:
                obs_folder = self.obs_controller.get_recording_folder()
            
            if not obs_folder:
                self.logger.error("No OBS recording folder found")
                return
            
            obs_path = Path(obs_folder)
            if not obs_path.exists():
                self.logger.error(f"OBS recording folder does not exist: {obs_folder}")
                return
            
            # Find the latest video file
            video_extensions = ['.mkv', '.mp4', '.avi', '.mov', '.flv']
            video_files = []
            
            for ext in video_extensions:
                video_files.extend(obs_path.glob(f'*{ext}'))
            
            if not video_files:
                self.logger.warning("No video files found in OBS recording folder")
                return
            
            # Get the latest file (by modification time)
            latest_file = max(video_files, key=lambda x: x.stat().st_mtime)
            
            # Check if this file was created after we started recording
            if self.current_session.get('obs_start_time'):
                file_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                start_time = self.current_session['obs_start_time']
                
                if file_time < start_time:
                    self.logger.warning("Latest file is older than recording start time")
                    return
            
            # Copy to session folder
            dest_path = self.current_session['path'] / latest_file.name
            shutil.copy2(latest_file, dest_path)
            self.logger.info(f"Copied recording to session folder: {dest_path}")
            
            # Update session metadata
            self.current_session['obs_recordings'] = self.current_session.get('obs_recordings', [])
            self.current_session['obs_recordings'].append(str(latest_file))
            
            self.current_session['local_recordings'] = self.current_session.get('local_recordings', [])
            self.current_session['local_recordings'].append(str(dest_path.relative_to(self.recordings_path)))
            
        except Exception as e:
            self.logger.error(f"Failed to find and copy latest recording: {e}")
    
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
        """List all recording sessions with frontend-compatible metadata"""
        sessions = []
        if self.recordings_path.exists():
            for session_dir in self.recordings_path.iterdir():
                if session_dir.is_dir():
                    # Try to load existing metadata first
                    metadata = self.load_session_metadata(session_dir)
                    
                    if metadata:
                        # Use existing metadata if it follows frontend format
                        if all(key in metadata for key in ['id', 'title', 'date', 'duration', 'size']):
                            sessions.append(metadata)
                            continue
                    
                    # Generate basic session info for backwards compatibility
                    video_files = [f for f in session_dir.iterdir() if f.is_file() and f.suffix.lower() in ['.mkv', '.mp4', '.avi', '.mov']]
                    
                    # Calculate total size
                    total_size = sum(f.stat().st_size for f in session_dir.iterdir() if f.is_file())
                    if total_size >= 1024**3:  # GB
                        size_str = f"{total_size / (1024**3):.1f} GB"
                    elif total_size >= 1024**2:  # MB
                        size_str = f"{total_size / (1024**2):.1f} MB"
                    else:  # Bytes/KB
                        size_str = f"{total_size / 1024:.1f} KB"
                    
                    # Create relative paths for video files
                    local_recordings = [str(session_dir.name + '/' + f.name) for f in video_files]
                    
                    session_info = {
                        'id': str(hash(session_dir.name)),
                        'title': session_dir.name,
                        'date': datetime.fromtimestamp(session_dir.stat().st_ctime).strftime('%Y-%m-%d'),
                        'duration': '0:00:00',  # Unknown for old sessions
                        'size': size_str,
                        'views': 0,
                        'thumbnail': '',
                        'platforms': ['Local Recording'],
                        'status': 'ready',
                        'hasTranscription': False,
                        'hasHighlights': False,
                        'hasShorts': False,
                        'categories': ['General'],
                        'isManualUpload': False,
                        'technical': {
                            'session_path': str(session_dir),
                            'local_recordings': local_recordings,
                            'files': [f.name for f in session_dir.iterdir() if f.is_file()],
                            'file_size_bytes': total_size
                        }
                    }
                    sessions.append(session_info)
        
        # Sort by date (newest first)
        sessions.sort(key=lambda x: x['date'], reverse=True)
        return sessions
    
    def load_session_metadata(self, session_path):
        """Load session metadata from session_metadata.json file"""
        try:
            import json
            metadata_file = Path(session_path) / 'session_metadata.json'
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            else:
                self.logger.debug(f"No metadata file found at: {metadata_file}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to load session metadata from {session_path}: {e}")
            return None
    
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
        """Save session metadata to file in format matching frontend Recording interface"""
        if not self.current_session:
            self.logger.warning("No current session to save metadata for")
            return False
        
        try:
            import json
            import os
            
            # Calculate session duration
            duration = "0:00:00"
            if self.current_session.get('end_time') and self.current_session.get('start_time'):
                duration_seconds = (self.current_session['end_time'] - self.current_session['start_time']).total_seconds()
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                seconds = int(duration_seconds % 60)
                duration = f"{hours}:{minutes:02d}:{seconds:02d}"
            elif self.current_session.get('obs_start_time'):
                # If recording is still active, calculate from start time to now
                duration_seconds = (datetime.now() - self.current_session['obs_start_time']).total_seconds()
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                seconds = int(duration_seconds % 60)
                duration = f"{hours}:{minutes:02d}:{seconds:02d}"
            
            # Calculate file size
            total_size = 0
            size_str = "0 MB"
            if self.current_session.get('local_recordings'):
                for recording_path in self.current_session['local_recordings']:
                    full_path = self.recordings_path / recording_path
                    if full_path.exists():
                        total_size += full_path.stat().st_size
                
                if total_size > 0:
                    if total_size >= 1024**3:  # GB
                        size_str = f"{total_size / (1024**3):.1f} GB"
                    else:  # MB
                        size_str = f"{total_size / (1024**2):.1f} MB"
            
            # Determine recording status for frontend
            frontend_status = "processing"
            if self.current_session.get('status') == 'stopped':
                frontend_status = "ready"
            elif self.current_session.get('status') == 'recording':
                frontend_status = "processing"
            
            # Detect platforms based on OBS setup or session data
            platforms = []
            if self.obs_controller.is_connected():
                stream_status = self.obs_controller.get_stream_status()
                if stream_status and stream_status.get('active'):
                    platforms.append('OBS Stream')
                else:
                    platforms.append('OBS Recording')
            
            # Add any additional platforms from metadata
            if additional_metadata and 'platforms' in additional_metadata:
                platforms.extend(additional_metadata['platforms'])
            
            if not platforms:
                platforms = ['Local Recording']
            
            # Generate categories based on session name and metadata
            categories = []
            session_name_lower = self.current_session['name'].lower()
            
            # Auto-detect categories from session name
            if 'gaming' in session_name_lower or 'game' in session_name_lower:
                categories.append('Gaming')
            if 'tutorial' in session_name_lower or 'education' in session_name_lower:
                categories.append('Education')
            if 'chat' in session_name_lower or 'discussion' in session_name_lower:
                categories.append('Just Chatting')
            if 'programming' in session_name_lower or 'coding' in session_name_lower:
                categories.append('Programming')
            if 'music' in session_name_lower:
                categories.append('Music')
            
            # Add categories from additional metadata
            if additional_metadata and 'categories' in additional_metadata:
                categories.extend(additional_metadata['categories'])
            
            # Default category if none detected
            if not categories:
                categories = ['General']
            
            # Remove duplicates
            categories = list(set(categories))
            
            # Create metadata in frontend Recording format
            frontend_metadata = {
                # Core Recording interface fields
                "id": str(hash(self.current_session['name'])),  # Generate consistent ID
                "title": self.current_session['name'],
                "date": self.current_session['start_time'].strftime('%Y-%m-%d'),
                "duration": duration,
                "size": size_str,
                "views": 0,  # Initial views count
                "thumbnail": additional_metadata.get('thumbnail', '') if additional_metadata else '',
                "platforms": platforms,
                "status": frontend_status,
                "hasTranscription": False,  # Will be updated when transcription is generated
                "hasHighlights": False,     # Will be updated when highlights are generated
                "hasShorts": False,         # Will be updated when shorts are generated
                "categories": categories,
                "isManualUpload": False,    # This is an OBS recording, not manual upload
                
                # Additional technical metadata for backend use
                "technical": {
                    "session_path": str(self.current_session['path']),
                    "start_time_iso": self.current_session['start_time'].isoformat(),
                    "end_time_iso": self.current_session.get('end_time').isoformat() if self.current_session.get('end_time') else None,
                    "obs_recording_folder": self.current_session.get('obs_recording_folder'),
                    "obs_recordings": self.current_session.get('obs_recordings', []),
                    "local_recordings": self.current_session.get('local_recordings', []),
                    "file_size_bytes": total_size
                }
            }
            
            # Add any additional metadata
            if additional_metadata:
                frontend_metadata["additional"] = additional_metadata
            
            # Save to session_metadata.json
            metadata_file = self.current_session['path'] / 'session_metadata.json'
            with open(metadata_file, 'w') as f:
                json.dump(frontend_metadata, f, indent=2, default=str)
            
            self.logger.info(f"Session metadata saved to: {metadata_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save session metadata: {e}")
            return False
