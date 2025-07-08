#!/usr/bin/env python3
"""
Production Audio Service for StreamAI
Handles audio processing from client-side uploads instead of local audio capture
"""

import os
import sys
import time
import tempfile
import threading
from datetime import datetime
from pathlib import Path

# Add the realtime_audio directory to the path
sys.path.append(os.path.dirname(__file__))

try:
    from transcription import Transcription
    import numpy as np
    import requests
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("cd realtime_audio && pip install -r requirements.txt")
    sys.exit(1)

class ProductionAudioService:
    """Production audio service that processes uploaded audio chunks from frontend"""
    
    def __init__(self, api_url="http://localhost:5001"):
        self.api_url = api_url
        self.transcription_system = None
        self.is_running = False
        self.is_listening = False  # Simulated for compatibility
        
        # Audio parameters for processing uploaded chunks
        self.sample_rate = 16000
        self.supported_formats = ['wav', 'mp3', 'ogg', 'webm']
        
        print("🎤 Production Audio Service (Client Upload Mode)")
        print("=" * 50)
    
    def start_service(self):
        """Start the transcription service"""
        try:
            print("\n📝 Initializing Whisper transcription system...")
            self.transcription_system = Transcription(
                model_name="base",
                device="cpu"  # Use CPU for production compatibility
            )
            
            self.is_running = True
            print("✅ Transcription service started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start transcription service: {e}")
            return False
    
    def stop_service(self):
        """Stop the transcription service"""
        try:
            self.is_running = False
            self.is_listening = False
            print("🛑 Transcription service stopped")
            return True
        except Exception as e:
            print(f"❌ Error stopping service: {e}")
            return False
    
    def start_listening(self):
        """Simulate starting to listen (for API compatibility)"""
        if not self.is_running:
            return False
        
        self.is_listening = True
        print("🎧 Started 'listening' mode (ready to process uploaded audio)")
        
        # Add a mock transcription to demonstrate the system is working
        self._add_mock_transcription()
        return True
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        print("⏹️  Stopped listening mode")
        return True
    
    def process_audio_file(self, audio_file_path, groq_api_key=None):
        """Process an uploaded audio file and return transcription"""
        if not self.is_running:
            raise Exception("Service is not running")
        
        try:
            print(f"🎵 Processing audio file: {audio_file_path}")
            
            # Load and preprocess audio
            audio_data = self.transcription_system.load_audio(audio_file_path)
            
            if audio_data is None or len(audio_data) == 0:
                raise Exception("Failed to load audio data")
            
            # Transcribe the audio
            raw_transcript = self.transcription_system.transcribe_chunk(audio_data)
            
            if not raw_transcript or raw_transcript.strip() == "":
                print("⚠️  No speech detected in audio chunk")
                return None
            
            print(f"📝 Raw transcript: {raw_transcript}")
            
            # Send to API server for processing and refinement
            self._send_transcription_to_api(raw_transcript)
            
            return raw_transcript
            
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            raise e
    
    def process_audio_blob(self, audio_blob_data, groq_api_key=None):
        """Process audio data from browser blob"""
        try:
            # Save blob to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_blob_data)
                temp_path = temp_file.name
            
            try:
                # Process the temporary file
                result = self.process_audio_file(temp_path, groq_api_key)
                return result
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"❌ Error processing audio blob: {e}")
            raise e
    
    def _add_mock_transcription(self):
        """Add a mock transcription to demonstrate the system is working"""
        try:
            mock_transcript = "Audio capture is now simulated in production. The system is ready to process real audio uploaded from the frontend."
            self._send_transcription_to_api(mock_transcript, message_type="system")
        except Exception as e:
            print(f"⚠️  Could not send mock transcription: {e}")
    
    def _send_transcription_to_api(self, transcript, message_type="raw"):
        """Send transcription to the API server"""
        try:
            # Send the transcription to the API server for queuing
            response = requests.post(
                f"{self.api_url}/api/transcription/add",
                json={
                    "transcription": transcript,
                    "type": message_type,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Sent transcription to API: {transcript[:50]}...")
            else:
                print(f"⚠️  API responded with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending transcription to API: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def get_listening_status(self):
        """Get current listening status"""
        return {
            "is_running": self.is_running,
            "is_listening": self.is_listening,
            "mode": "production",
            "audio_source": "client_upload",
            "message": "Ready to process uploaded audio from frontend" if self.is_running else "Service not running"
        }

# Global service instance
production_audio_service = ProductionAudioService()

def get_production_service():
    """Get the global production audio service instance"""
    return production_audio_service

if __name__ == "__main__":
    # Test the production service
    service = ProductionAudioService()
    
    if service.start_service():
        print("\n🚀 Production audio service is ready!")
        print("This service processes audio uploaded from the frontend.")
        print("In production, audio capture happens in the browser, not on the server.")
        
        # Start listening mode
        service.start_listening()
        
        # Keep the service running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down service...")
            service.stop_service()
    else:
        print("❌ Failed to start production audio service")
        sys.exit(1)
