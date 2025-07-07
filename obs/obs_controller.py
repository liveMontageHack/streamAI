import asyncio
import logging
from datetime import datetime
from obswebsocket import obsws, requests
from config import config

class OBSController:
    """Controller for OBS WebSocket API integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ws = None
        self.connected = False
        self.recording_active = False
        
    async def connect(self):
        """Connect to OBS WebSocket"""
        try:
            connection_info = config.get_obs_connection_info()
            self.ws = obsws(
                connection_info['host'], 
                connection_info['port'], 
                connection_info['password']
            )
            self.ws.connect()
            self.connected = True
            self.logger.info("Successfully connected to OBS WebSocket")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to OBS: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from OBS WebSocket"""
        if self.ws and self.connected:
            try:
                self.ws.disconnect()
                self.connected = False
                self.logger.info("Disconnected from OBS WebSocket")
            except Exception as e:
                self.logger.error(f"Error disconnecting from OBS: {e}")
    
    def is_connected(self):
        """Check if connected to OBS"""
        return self.connected
    
    def get_version_info(self):
        """Get OBS version information"""
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return None
        
        try:
            response = self.ws.call(requests.GetVersion())
            self.logger.info(f"OBS Version: {response.getObsVersion()}")
            return response.datain
        except Exception as e:
            self.logger.error(f"Failed to get OBS version: {e}")
            return None
    
    def get_current_scene(self):
        """Get current active scene"""
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return None
        
        try:
            response = self.ws.call(requests.GetCurrentProgramScene())
            scene_name = response.datain['currentProgramSceneName']
            self.logger.info(f"Current scene: {scene_name}")
            return scene_name
        except Exception as e:
            self.logger.error(f"Failed to get current scene: {e}")
            return None
    
    def get_scenes_list(self):
        """Get list of all scenes"""
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return []
        
        try:
            response = self.ws.call(requests.GetSceneList())
            scenes = [scene['sceneName'] for scene in response.datain['scenes']]
            self.logger.info(f"Available scenes: {scenes}")
            return scenes
        except Exception as e:
            self.logger.error(f"Failed to get scenes list: {e}")
            return []
    
    def start_recording(self):
        """Start recording in OBS"""
        self.logger.debug("Starting recording...")
        
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return False
        
        try:
            self.logger.debug("Checking if already recording...")
            # Check if already recording
            status = self.ws.call(requests.GetRecordStatus())
            self.logger.debug(f"Current record status: {status.datain}")
            
            if status.datain['outputActive']:
                self.logger.warning("Recording is already active")
                return True
            
            self.logger.debug("Calling StartRecord...")
            # Start recording
            self.ws.call(requests.StartRecord())
            self.recording_active = True
            self.logger.info("Recording started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop recording in OBS"""
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return False
        
        try:
            # Check if recording is active
            status = self.ws.call(requests.GetRecordStatus())
            if not status.datain['outputActive']:
                self.logger.warning("No active recording to stop")
                return True
            
            # Stop recording
            response = self.ws.call(requests.StopRecord())
            self.recording_active = False
            self.logger.info("Recording stopped successfully")
            
            # Get the output file path if available
            if 'outputPath' in response.datain:
                output_path = response.datain['outputPath']
                self.logger.info(f"Recording saved to: {output_path}")
                return output_path
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return False
    
    def get_recording_status(self):
        """Get current recording status"""
        self.logger.debug("Getting recording status...")
        
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return None
        
        try:
            self.logger.debug("Calling GetRecordStatus...")
            response = self.ws.call(requests.GetRecordStatus())
            self.logger.debug(f"GetRecordStatus response: {response.datain}")
            
            status = {
                'active': response.datain['outputActive'],
                'paused': response.datain.get('outputPaused', False),
                'timecode': response.datain.get('outputTimecode', '00:00:00'),
                'bytes': response.datain.get('outputBytes', 0)
            }
            self.logger.debug(f"Parsed status: {status}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to get recording status: {e}")
            return None
    
    def get_stream_status(self):
        """Get current streaming status"""
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return None
        
        try:
            response = self.ws.call(requests.GetStreamStatus())
            status = {
                'active': response.datain['outputActive'],
                'reconnecting': response.datain.get('outputReconnecting', False),
                'timecode': response.datain.get('outputTimecode', '00:00:00'),
                'duration': response.datain.get('outputDuration', 0),
                'congestion': response.datain.get('outputCongestion', 0),
                'bytes': response.datain.get('outputBytes', 0),
                'skipped_frames': response.datain.get('outputSkippedFrames', 0),
                'total_frames': response.datain.get('outputTotalFrames', 0)
            }
            return status
        except Exception as e:
            self.logger.error(f"Failed to get stream status: {e}")
            return None
    
    def get_audio_sources(self):
        """Get list of audio sources"""
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return []
        
        try:
            response = self.ws.call(requests.GetInputList())
            audio_sources = []
            
            for input_item in response.datain['inputs']:
                input_kind = input_item['inputKind']
                # Check if it's an audio source
                if 'audio' in input_kind.lower() or input_kind in ['wasapi_input_capture', 'wasapi_output_capture', 'pulse_input_capture', 'pulse_output_capture']:
                    audio_sources.append({
                        'name': input_item['inputName'],
                        'kind': input_kind
                    })
            
            self.logger.info(f"Audio sources found: {[src['name'] for src in audio_sources]}")
            return audio_sources
        except Exception as e:
            self.logger.error(f"Failed to get audio sources: {e}")
            return []
    
    def get_recording_folder(self):
        """Get the current recording folder path from OBS"""
        if not self.connected:
            self.logger.error("Not connected to OBS")
            return None
        
        try:
            response = self.ws.call(requests.GetRecordDirectory())
            folder_path = response.datain['recordDirectory']
            self.logger.info(f"OBS recording folder: {folder_path}")
            return folder_path
        except Exception as e:
            self.logger.error(f"Failed to get recording folder: {e}")
            return None
