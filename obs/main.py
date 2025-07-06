#!/usr/bin/env python3
"""
StreamAI Recording App - Main Entry Point

This application provides core functionality for recording sessions from OBS
and integrating with YouTube API for streaming platform features.

Usage:
    python main.py [command] [options]

Commands:
    status      - Show system status
    start       - Start recording session
    stop        - Stop recording session
    list        - List all recording sessions
    obs-data    - Get current OBS data
    youtube     - Get YouTube data
    test        - Run system tests
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from recording_manager import RecordingManager

class StreamAIApp:
    """Main application class"""
    
    def __init__(self):
        self.recording_manager = RecordingManager()
        self.initialized = False
    
    async def initialize(self):
        """Initialize the application"""
        if not self.initialized:
            print("Initializing StreamAI Recording App...")
            success = await self.recording_manager.initialize()
            self.initialized = success
            return success
        return True
    
    async def show_status(self):
        """Show system status"""
        if not await self.initialize():
            print("❌ Failed to initialize application")
            return False
        
        status = self.recording_manager.get_system_status()
        
        print("\n=== StreamAI System Status ===")
        print(f"Timestamp: {status['timestamp']}")
        print(f"OBS Connected: {'✅' if status['obs_connected'] else '❌'}")
        print(f"YouTube Authenticated: {'✅' if status['youtube_authenticated'] else '❌'}")
        print(f"Recordings Path: {status['recordings_path']}")
        
        if status['current_session']:
            print(f"\nCurrent Session: {status['current_session']['name']}")
            print(f"Session Status: {status['current_session']['status']}")
        else:
            print("\nNo active session")
        
        if status['obs_connected']:
            print(f"\n--- OBS Information ---")
            if status.get('current_scene'):
                print(f"Current Scene: {status['current_scene']}")
            
            recording_status = status.get('recording_status')
            if recording_status:
                print(f"Recording Active: {'✅' if recording_status['active'] else '❌'}")
                if recording_status['active']:
                    print(f"Recording Time: {recording_status['timecode']}")
            
            stream_status = status.get('stream_status')
            if stream_status:
                print(f"Streaming Active: {'✅' if stream_status['active'] else '❌'}")
                if stream_status['active']:
                    print(f"Stream Time: {stream_status['timecode']}")
            
            audio_sources = status.get('audio_sources', [])
            if audio_sources:
                print(f"Audio Sources: {len(audio_sources)} found")
                for source in audio_sources:
                    print(f"  - {source['name']} ({source['kind']})")
        
        return True
    
    async def start_recording(self, session_name=None):
        """Start a recording session"""
        if not await self.initialize():
            print("❌ Failed to initialize application")
            return False
        
        print("Starting recording session...")
        success = await self.recording_manager.start_recording_session(session_name)
        
        if success:
            session_info = self.recording_manager.get_current_session_info()
            print(f"✅ Recording session started: {session_info['name']}")
            print(f"Session path: {session_info['path']}")
            return True
        else:
            print("❌ Failed to start recording session")
            return False
    
    async def stop_recording(self):
        """Stop the current recording session"""
        if not await self.initialize():
            print("❌ Failed to initialize application")
            return False
        
        print("Stopping recording session...")
        success = await self.recording_manager.stop_recording_session()
        
        if success:
            session_info = self.recording_manager.get_current_session_info()
            if session_info:
                print(f"✅ Recording session stopped: {session_info['name']}")
                
                # Save session metadata
                self.recording_manager.save_session_metadata()
                print("Session metadata saved")
            else:
                print("✅ Recording stopped")
            return True
        else:
            print("❌ Failed to stop recording session")
            return False
    
    async def list_sessions(self):
        """List all recording sessions"""
        sessions = self.recording_manager.list_sessions()
        
        if not sessions:
            print("No recording sessions found")
            return True
        
        print(f"\n=== Recording Sessions ({len(sessions)} found) ===")
        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session['name']}")
            print(f"   Created: {session['created']}")
            print(f"   Path: {session['path']}")
            print(f"   Files: {len(session['files'])} files")
            if session['files']:
                for file in session['files'][:3]:  # Show first 3 files
                    print(f"     - {file}")
                if len(session['files']) > 3:
                    print(f"     ... and {len(session['files']) - 3} more")
            print()
        
        return True
    
    async def get_obs_data(self):
        """Get and display current OBS data"""
        if not await self.initialize():
            print("❌ Failed to initialize application")
            return False
        
        data = self.recording_manager.get_obs_data()
        if not data:
            print("❌ Failed to get OBS data")
            return False
        
        print("\n=== OBS Data ===")
        print(json.dumps(data, indent=2, default=str))
        return True
    
    async def get_youtube_data(self, query=None, channel_id=None):
        """Get and display YouTube data"""
        if not await self.initialize():
            print("❌ Failed to initialize application")
            return False
        
        data = self.recording_manager.get_youtube_data(query, channel_id)
        if not data:
            print("❌ Failed to get YouTube data")
            return False
        
        print("\n=== YouTube Data ===")
        print(json.dumps(data, indent=2, default=str))
        return True
    
    async def run_tests(self):
        """Run system tests"""
        print("Running StreamAI system tests...\n")
        
        # Test 1: Initialization
        print("Test 1: Application Initialization")
        success = await self.initialize()
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}\n")
        
        if not success:
            print("Cannot continue tests without successful initialization")
            return False
        
        # Test 2: OBS Connection
        print("Test 2: OBS Connection")
        obs_connected = self.recording_manager.obs_controller.is_connected()
        print(f"Result: {'✅ PASS' if obs_connected else '❌ FAIL'}")
        if obs_connected:
            version = self.recording_manager.obs_controller.get_version_info()
            print(f"OBS Version: {version}")
        print()
        
        # Test 3: YouTube API
        print("Test 3: YouTube API Authentication")
        youtube_auth = self.recording_manager.youtube_api.is_authenticated()
        print(f"Result: {'✅ PASS' if youtube_auth else '❌ FAIL'}")
        if youtube_auth:
            api_valid = self.recording_manager.youtube_api.validate_api_key()
            print(f"API Key Valid: {'✅ YES' if api_valid else '❌ NO'}")
        print()
        
        # Test 4: Recording functionality (if OBS connected)
        if obs_connected:
            print("Test 4: Recording Functionality")
            try:
                # Create a test session
                session = self.recording_manager.create_session("test_session")
                print(f"Test session created: {session['name']}")
                
                # Check recording status
                status = self.recording_manager.obs_controller.get_recording_status()
                print(f"Recording status retrieved: {'✅ YES' if status else '❌ NO'}")
                
                print("Result: ✅ PASS")
            except Exception as e:
                print(f"Result: ❌ FAIL - {e}")
            print()
        
        # Test 5: File system
        print("Test 5: File System Access")
        try:
            recordings_path = self.recording_manager.recordings_path
            recordings_path.mkdir(parents=True, exist_ok=True)
            test_file = recordings_path / "test.txt"
            test_file.write_text("test")
            test_file.unlink()
            print("Result: ✅ PASS")
        except Exception as e:
            print(f"Result: ❌ FAIL - {e}")
        print()
        
        print("System tests completed!")
        return True
    
    async def cleanup(self):
        """Cleanup application resources"""
        if self.initialized:
            await self.recording_manager.cleanup()

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="StreamAI Recording App - OBS and YouTube Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('command', 
                       choices=['status', 'start', 'stop', 'list', 'obs-data', 'youtube', 'test'],
                       help='Command to execute')
    
    parser.add_argument('--session-name', '-s',
                       help='Name for the recording session (for start command)')
    
    parser.add_argument('--query', '-q',
                       help='Search query (for youtube command)')
    
    parser.add_argument('--channel-id', '-c',
                       help='YouTube channel ID (for youtube command)')
    
    args = parser.parse_args()
    
    app = StreamAIApp()
    try:
        match args.command:
            case 'start':
                await app.start_recording(args.session_name)
            case 'status':
                await app.show_status()
            case 'start':
                await app.start_recording(args.session_name)
            case 'stop':
                await app.stop_recording()
            case 'list':
                await app.list_sessions()
            case 'obs-data':
                await app.get_obs_data()
            case 'youtube':
                await app.get_youtube_data(args.query, args.channel_id)
            case 'test':
                await app.run_tests()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        await app.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
