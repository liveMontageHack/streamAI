#!/usr/bin/env python3
"""
Real-time Audio Transcription Service for StreamAI
Connects audio capture -> Whisper transcription -> API server -> Frontend chat
"""

import sys
import os
import time
import signal
import threading
from datetime import datetime

# Add the realtime_audio directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'realtime_audio'))

try:
    from transcription import Transcription
    from audio_capture import start_stream
    import numpy as np
    import requests
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("cd realtime_audio && pip install -r requirements.txt")
    sys.exit(1)

class RealTimeTranscriptionService:
    """Real-time audio transcription service with optimized chunking"""
    
    def __init__(self, api_url="http://localhost:5001"):
        self.api_url = api_url
        self.transcription_system = None
        self.audio_stream = None
        self.is_running = False
        self.is_listening = False
        
        # Audio parameters optimized for real-time processing
        self.sample_rate = 16000
        self.chunk_size = 1024  # Small chunks for low latency
        self.buffer_duration = 2  # Process audio every 2 seconds for responsiveness
        
        print("🎤 Real-Time Transcription Service")
        print("=" * 50)
    
    def start_service(self):
        """Start the transcription service"""
        try:
            print("\n📝 Initializing Whisper transcription system...")
            self.transcription_system = Transcription(
                sample_rate=self.sample_rate,
                buffer_duration=self.buffer_duration,
                api_url=self.api_url
            )
            
            print("🔊 Setting up audio capture...")
            self.setup_audio_capture()
            
            self.is_running = True
            print("\n✅ Service initialized successfully!")
            print(f"🔗 API URL: {self.api_url}")
            print("\n📱 Frontend Integration:")
            print("   1. Start API server: python obs/api_server.py")
            print("   2. Start frontend: cd frontend && npm run dev")
            print("   3. Click 'Start Listening' in the Transcription tab")
            print("\n⚠️  Press Ctrl+C to stop service...")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error starting service: {e}")
            return False
    
    def setup_audio_capture(self):
        """Set up audio capture with your existing audio_capture.py"""
        def audio_callback(audio_chunk):
            """Process each audio chunk in real-time"""
            if self.is_listening and len(audio_chunk) > 0:
                # Convert to float32 if needed
                if audio_chunk.dtype != np.float32:
                    audio_chunk = audio_chunk.astype(np.float32)
                
                # Send to transcription system
                if self.transcription_system:
                    self.transcription_system.add_audio(audio_chunk)
        
        # Use your existing audio capture function
        self.audio_stream = start_stream(
            callback=audio_callback,
            samplerate=self.sample_rate,
            blocksize=self.chunk_size
        )
        
        print(f"✓ Audio stream started (sample rate: {self.sample_rate}Hz, chunk size: {self.chunk_size})")
    
    def start_listening(self):
        """Start audio processing (called when frontend clicks 'Start Listening')"""
        if not self.is_running:
            print("❌ Service not running. Call start_service() first.")
            return False
        
        self.is_listening = True
        print(f"🎙️  [{datetime.now().strftime('%H:%M:%S')}] Started listening for audio...")
        return True
    
    def stop_listening(self):
        """Stop audio processing (called when frontend clicks 'Stop Listening')"""
        self.is_listening = False
        print(f"⏹️  [{datetime.now().strftime('%H:%M:%S')}] Stopped listening.")
        return True
    
    def get_listening_status(self):
        """Get current listening status"""
        return {
            "is_running": self.is_running,
            "is_listening": self.is_listening,
            "timestamp": datetime.now().isoformat()
        }
    
    def stop_service(self):
        """Stop the entire service"""
        print("\n🛑 Stopping transcription service...")
        
        self.is_listening = False
        self.is_running = False
        
        if self.audio_stream:
            print("🔇 Stopping audio capture...")
            self.audio_stream.stop()
            self.audio_stream.close()
        
        if self.transcription_system:
            print("📝 Stopping transcription system...")
            self.transcription_system.stop()
        
        print("✅ Service stopped.")

# Global service instance
transcription_service = RealTimeTranscriptionService()

def main():
    """Main entry point for standalone operation"""
    
    # Check if API server is running
    try:
        response = requests.get(f"{transcription_service.api_url}/api/health", timeout=2)
        if response.ok:
            print("✅ API server is running")
        else:
            print("⚠️  API server responded but with error")
    except:
        print("⚠️  Warning: API server may not be running")
        print("   Make sure to start it: python obs/api_server.py")
    
    # Start the service
    if transcription_service.start_service():
        # Start listening immediately for standalone mode
        transcription_service.start_listening()
        
        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            transcription_service.stop_service()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Keep running
        try:
            while transcription_service.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            transcription_service.stop_service()

if __name__ == "__main__":
    main()
