import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the recording app"""
    
    def __init__(self):
        self.setup_logging()
        self.validate_config()
    
    # YouTube API Configuration
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # OBS WebSocket Configuration
    OBS_HOST = os.getenv('OBS_HOST', 'localhost')
    OBS_PORT = int(os.getenv('OBS_PORT', 4455))
    OBS_PASSWORD = os.getenv('OBS_PASSWORD')
    
    # Recording Configuration
    RECORDINGS_PATH = Path(os.getenv('RECORDINGS_PATH', './recordings'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.LOG_LEVEL.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('recording_app.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_config(self):
        """Validate required configuration values"""
        if not self.YOUTUBE_API_KEY:
            self.logger.warning("YouTube API key not found. YouTube features will be disabled.")
        
        if not self.OBS_PASSWORD:
            self.logger.warning("OBS WebSocket password not set. Connection may fail.")
        
        # Create recordings directory if it doesn't exist
        self.RECORDINGS_PATH.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Recordings will be saved to: {self.RECORDINGS_PATH.absolute()}")
    
    def get_obs_connection_info(self):
        """Get OBS connection information"""
        return {
            'host': self.OBS_HOST,
            'port': self.OBS_PORT,
            'password': self.OBS_PASSWORD
        }
    
    def get_youtube_api_key(self):
        """Get YouTube API key"""
        return self.YOUTUBE_API_KEY
    
    def get_recordings_path(self):
        """Get recordings directory path"""
        return self.RECORDINGS_PATH

# Global config instance
config = Config()
